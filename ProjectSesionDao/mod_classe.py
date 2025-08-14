class Activite:
    def __init__(self, condition,reponse ):

        self.condition = condition
        self.reponse =reponse


    def __str__(self):
        return f"Activite(id={self.id}, condition={self.condition}, reponse={self.reponse})"