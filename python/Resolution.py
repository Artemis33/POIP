from WarehouseLoader import WarehouseLoader
from WarehouseSolution import WarehouseSolution


class Resolution:
    """
    Classe mère pour les algorithmes de résolution de problème d'entrepôt.
    
    Attributes
    ----------
    warehouse_loader : WarehouseLoader
        Instance de WarehouseLoader pour charger les donnees de l'entrepot.
    solution : WarehouseSolution
        Instance de WarehouseSolution pour stocker la solution du probleme.

    
    Methods
    -------
    __init__(self, instance_name: str)
        Initialise la classe Resolution avec le nom de l'instance.
    resolve(self)
        Methode a implementer dans les sous-classes pour resoudre le probleme.  
    """

    def __init__(self, instance_name: str):
        """
        Initializes the Resolution class with the given instance name.
        
        @param instance_name: str - The name of the warehouse instance to load.
        """
        self.warehouse_loader = WarehouseLoader(instance_name)
        self.solution = WarehouseSolution(instance_name, self.__class__.__name__)

        self.resolve()
        self.solution.save_solution()

    def resolve(self):
        """
        Resolves the warehouse problem.
        This method should be implemented in subclasses.
        """
        raise NotImplementedError("Method resolve() must be implemented in subclass.")