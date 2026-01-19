/*
 * @(#)src/demo/jfc/SampleTree/src/SampleTreeModel.java, swing, dsdev 1.11
 * ===========================================================================
 * Licensed Materials - Property of IBM
 * "Restricted Materials of IBM"
 *
 * IBM SDK, Java(tm) 2 Technology Edition, v5.0
 * (C) Copyright IBM Corp. 1998, 2005. All Rights Reserved
 *
 * US Government Users Restricted Rights - Use, duplication or disclosure
 * restricted by GSA ADP Schedule Contract with IBM Corp.
 * ===========================================================================
 */

/*
 * ===========================================================================
 (C) Copyright Sun Microsystems Inc, 1992, 2004. All rights reserved.
 * ===========================================================================
 */





/*
 * @(#)SampleTreeModel.java	1.9 02/06/13
 */

import javax.swing.tree.DefaultTreeModel;
import javax.swing.tree.TreeNode;
import javax.swing.tree.TreePath;
import javax.swing.tree.DefaultMutableTreeNode;
import java.awt.Color;

/**
  * SampleTreeModel extends JTreeModel to extends valueForPathChanged.
  * This method is called as a result of the user editing a value in
  * the tree.  If you allow editing in your tree, are using TreeNodes
  * and the user object of the TreeNodes is not a String, then you're going
  * to have to subclass JTreeModel as this example does.
  *
  * @version 1.9 06/13/02
  * @author Scott Violet
  */

public class SampleTreeModel extends DefaultTreeModel
{
    /**
      * Creates a new instance of SampleTreeModel with newRoot set
      * to the root of this model.
      */
    public SampleTreeModel(TreeNode newRoot) {
	super(newRoot);
    }

    /**
      * Subclassed to message setString() to the changed path item.
      */
    public void valueForPathChanged(TreePath path, Object newValue) {
	/* Update the user object. */
	DefaultMutableTreeNode      aNode = (DefaultMutableTreeNode)path.getLastPathComponent();
	SampleData    sampleData = (SampleData)aNode.getUserObject();

	sampleData.setString((String)newValue);
	/* UUUhhhhh, pretty colors. */
	sampleData.setColor(Color.green);

	/* Since we've changed how the data is to be displayed, message
	   nodeChanged. */
	nodeChanged(aNode);
    }
}
