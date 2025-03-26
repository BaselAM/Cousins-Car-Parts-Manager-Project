from PyQt5.QtWidgets import QFormLayout

# Constant for fixed label width
LABEL_WIDTH = 150

def fix_form_layout_labels(form_layout, width=LABEL_WIDTH):
    """Force every label in a QFormLayout to a constant width."""
    for i in range(form_layout.rowCount()):
        label_item = form_layout.itemAt(i, QFormLayout.LabelRole)
        if label_item and label_item.widget():
            label_item.widget().setFixedWidth(width)