package jxe2jar.vf;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.HashSet;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Locale;
import java.util.Map;
import java.util.Set;
import java.util.regex.Pattern;

import org.jetbrains.java.decompiler.api.plugin.Plugin;
import org.jetbrains.java.decompiler.main.extern.IVariableNameProvider;
import org.jetbrains.java.decompiler.main.extern.IVariableNamingFactory;
import org.jetbrains.java.decompiler.modules.decompiler.ExprProcessor;
import org.jetbrains.java.decompiler.modules.decompiler.vars.VarVersionPair;
import org.jetbrains.java.decompiler.struct.StructMethod;
import org.jetbrains.java.decompiler.struct.attr.StructLocalVariableTableAttribute;
import org.jetbrains.java.decompiler.struct.gen.MethodDescriptor;
import org.jetbrains.java.decompiler.struct.gen.VarType;
import org.jetbrains.java.decompiler.util.Pair;

/**
 * Vineflower's bundled JAD renamer ({@code --variable-renaming=jad --rename-parameters=true})
 * renames every variable it is handed, and it is handed every variable - the LocalVariableTable
 * names that {@code tools/donor_lvt.py} grafted from the MH2p donors included. The renamer API
 * never sees the current name (the string in the entry is the *type*), so the only way to keep
 * an LVT name is to not return a new one: this provider skips every slot the method's LVT names
 * and hands JAD-style names to the rest. It is picked up from the classpath (ServiceLoader) and
 * used whenever no {@code --variable-renaming} option is given.
 */
public final class LvtFirstRenamerPlugin implements Plugin {
  @Override public String id() { return "lvt-first-renamer"; }
  @Override public String description() { return "Keep LocalVariableTable names, JAD-style names for the rest"; }
  @Override public IVariableNamingFactory getRenamingFactory() { return LvtFirstNameProvider::new; }
}

final class LvtFirstNameProvider implements IVariableNameProvider {
  private static final Pattern GENERATED = Pattern.compile("var\\d+(_\\d+)?");
  private static final Set<String> RESERVED = Set.of(
      "abstract", "assert", "boolean", "break", "byte", "case", "catch", "char", "class", "const", "continue",
      "default", "do", "double", "else", "enum", "extends", "final", "finally", "float", "for", "goto", "if",
      "implements", "import", "instanceof", "int", "interface", "long", "native", "new", "package", "private",
      "protected", "public", "return", "short", "static", "strictfp", "super", "switch", "synchronized", "this",
      "throw", "throws", "transient", "try", "void", "volatile", "while", "true", "false", "null", "var", "record");
  private static final Map<String, String> PRIMITIVE_STEMS = Map.of(
      "int", "i", "long", "l", "float", "f", "double", "d", "boolean", "flag", "byte", "b", "char", "c", "short", "sh",
      "String", "s", "Object", "obj");

  private final int paramSlots;
  private final Set<Integer> lvtSlots = new HashSet<>();
  private final Set<String> used = new HashSet<>();
  private final Map<Integer, String> parameters = new HashMap<>();
  private final Map<String, Integer> counters = new HashMap<>();

  LvtFirstNameProvider(StructMethod method) {
    int slots = (method.getAccessFlags() & 8) == 0 ? 1 : 0;
    for (VarType t : MethodDescriptor.parseDescriptor(method.getDescriptor()).params) slots += t.stackSize;
    paramSlots = slots;
    StructLocalVariableTableAttribute lvt = method.getLocalVariableAttr();
    if (lvt != null) {
      lvt.getMapNames().forEach((pair, name) -> { lvtSlots.add(pair.var); used.add(name); });
    }
  }

  private static boolean real(String name) {
    return name != null && !name.isEmpty() && !GENERATED.matcher(name).matches();
  }

  @Override
  public synchronized Map<VarVersionPair, String> rename(Map<VarVersionPair, Pair<VarType, String>> entries) {
    List<VarVersionPair> keys = new ArrayList<>(entries.keySet());
    keys.sort((a, b) -> a.var != b.var ? a.var - b.var : a.version - b.version);
    Map<VarVersionPair, String> out = new LinkedHashMap<>();
    for (VarVersionPair v : keys) {
      String type = clean(entries.get(v).b);
      if ("this".equals(type) || lvtSlots.contains(v.var)) continue;  // LVT-named: Vineflower keeps its name
      out.put(v, v.var < paramSlots ? parameters.computeIfAbsent(v.var, k -> fresh(type)) : fresh(type));
    }
    return out;
  }

  @Override
  public synchronized String renameParameter(int flags, VarType type, String name, int index) {
    if (lvtSlots.contains(index) || real(name)) return name;
    return parameters.computeIfAbsent(index, k -> fresh(clean(ExprProcessor.getCastTypeName(type))));
  }

  @Override
  public synchronized void addParentContext(IVariableNameProvider parent) {
    if (parent instanceof LvtFirstNameProvider) used.addAll(((LvtFirstNameProvider) parent).used);
  }

  /** "java.util.List<String>" -> "List", "int[]..." -> "int[]" */
  private static String clean(String type) {
    if (type == null) return "object";
    int lt = type.indexOf('<');
    if (lt >= 0) type = type.substring(0, lt);
    type = type.replace("...", "[]");
    int dot = type.lastIndexOf('.');
    return dot >= 0 ? type.substring(dot + 1) : type;
  }

  /** JAD-like stem: i/l/f/d/flag/b/c for primitives, s for String, obj for Object, lower-cased simple class
   *  name otherwise; arrays "a" + element word. Then the first free of stem, stem1, stem2, ... */
  private String fresh(String type) {
    boolean array = type.contains("[]");
    String element = type.replace("[]", "");
    String stem = array ? "a" + element.toLowerCase(Locale.ENGLISH) : PRIMITIVE_STEMS.getOrDefault(element, element.toLowerCase(Locale.ENGLISH));
    if (stem.isEmpty() || !Character.isJavaIdentifierStart(stem.charAt(0))) stem = "var";
    String name = stem;
    while (used.contains(name) || RESERVED.contains(name)) name = stem + counters.merge(stem, 1, Integer::sum);
    used.add(name);
    return name;
  }
}
