@echo off
cd "\Storage Card\weme"
jar2jxe -le -noPrecompile -noCompileAheadOfTime -noStripBytecode -startupClass cases.Hello  -vmOption -jcl:foun11 cases.jar cases.jxe
echo Done
pause

