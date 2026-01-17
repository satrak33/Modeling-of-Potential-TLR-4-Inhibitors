from IPython.display import SVG, display
from rdkit.Chem import Draw

def draw(mol):
    d = Draw.MolDraw2DSVG(400, 200)
    d.drawOptions().addAtomIndices = True
    d.DrawMolecule(mol)
    d.FinishDrawing()

    return display(SVG(d.GetDrawingText()))