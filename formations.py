def rowup_formations():
    formations = []
    formations.append([[0, 0], [1, 0], [1, 1], [2, 1]])
    formations.append([[-1, -1], [0, -1], [0, 0], [1, 0]])
    formations.append([[0, 0], [1, 0], [1, -1], [2, -1]])
    formations.append([[-1, 1], [0, 1], [0, 0], [1, 0]])
    formations.append([[0, -1], [0, 0], [1, 0], [1, 1]])
    formations.append([[1, -1], [1, 0], [0, 0], [0, 1]])
    formations.append([[0, 0], [1, 0], [-1, 0]])
    formations.append([[0, 0], [2, 0], [1, 0]])
    return formations


def rowdown_formations():
    formations = []
    formations.append([[-2, -1], [-1, -1], [-1, 0], [0, 0]])
    formations.append([[-2, 1], [-1, 1], [-1, 0], [0, 0]])
    formations.append([[-1, 0], [0, 0], [0, -1], [1, -1]])
    formations.append([[-1, 0], [0, 0], [0, 1], [1, 1]])
    formations.append([[-1, -1], [-1, 0], [0, 0], [0, 1]])
    formations.append([[0, -1], [0, 0], [-1, 0], [-1, 1]])
    formations.append([[0, 0], [-1, 0], [-2, 0]])
    return formations


def colup_formations():
    formations = []
    formations.append([[0, 0], [0, 1], [1, 1], [1, 2]])
    formations.append([[0, 0], [0, 1], [-1, 1], [-1, 2]])
    formations.append([[0, 0], [0, -1], [0, 1]])
    formations.append([[0, 0], [0, 2], [0, 1]])
    return formations


def coldown_formations():
    formations = []
    formations.append([[-1, -2], [-1, -1], [0, -1], [0, 0]])
    formations.append([[1, -2], [1, -1], [0, -1], [0, 0]])
    formations.append([[0, 0], [0, -1], [0, -2]])
    return formations


def all_formations():
    formations = []
    # Wide diagonal left low
    formations.append([[0, 0], [1, 0], [1, 1], [2, 1]])
    formations.append([[-1, 0], [0, 0], [0, 1], [1, 1]])
    formations.append([[-1, -1], [0, -1], [0, 0], [1, 0]])
    formations.append([[-2, -1], [-1, -1], [-1, 0], [0, 0]])
    # Wide diagonal left high
    formations.append([[0, 0], [1, 0], [1, -1], [2, -1]])
    formations.append([[-1, 0], [0, 0], [0, -1], [1, -1]])
    formations.append([[-1, 1], [0, 1], [0, 0], [1, 0]])
    formations.append([[-2, 1], [-1, 1], [-1, 0], [0, 0]])
    # Tall diagonal left low
    formations.append([[0, 0], [0, 1], [1, 1], [1, 2]])
    formations.append([[0, -1], [0, 0], [1, 0], [1, 1]])
    formations.append([[-1, -1], [-1, 0], [0, 0], [0, 1]])
    formations.append([[-1, -2], [-1, -1], [0, -1], [0, 0]])
    # Wide diagonal left high
    formations.append([[0, 0], [0, 1], [-1, 1], [-1, 2]])
    formations.append([[0, -1], [0, 0], [-1, 0], [-1, 1]])
    formations.append([[1, -1], [1, 0], [0, 0], [0, 1]])
    formations.append([[1, -2], [1, -1], [0, -1], [0, 0]])

    # horizontal row
    formations.append([[0, 0], [-1, 0], [-2, 0]])
    formations.append([[0, 0], [1, 0], [-1, 0]])
    formations.append([[0, 0], [2, 0], [1, 0]])
    # vertical row
    formations.append([[0, 0], [0, -1], [0, -2]])
    formations.append([[0, 0], [0, -1], [0, 1]])
    formations.append([[0, 0], [0, 2], [0, 1]])
    return formations

def checkFormation(formation, row, column, rows, columns):
    valid = True
    newformation = []
    for vector in formation:
        vectorrow = vector[0]
        vectorcolumn = vector[1]
        if not (0 <= row + vectorrow < rows and 0 <= column + vectorcolumn < columns):
            valid = False
        else:
            newformation.append([vectorrow + row, vectorcolumn + column])
    return valid, newformation
