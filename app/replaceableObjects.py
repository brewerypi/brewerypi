from alembic.operations import Operations, MigrateOperation

# Concepts from: http://alembic.zzzcomputing.com/en/latest/cookbook.html#replaceable-objects.

class ReplaceableObject(object):
    def __init__(self, name, parameters, returns, sqlText):
        self.name = name
        self.parameters = parameters
        self.returns = returns
        self.sqlText = sqlText

class ReversibleOperation(MigrateOperation):
    def __init__(self, target):
        self.target = target

    @classmethod
    def invokeForTarget(cls, operations, target):
        op = cls(target)
        return operations.invoke(op)

    def reverse(self):
        raise NotImplementedError()

    @classmethod
    def _get_object_from_version(cls, operations, ident):
        version, objname = ident.split(".")
        module = operations.get_context().script.get_revision(version).module
        obj = getattr(module, objname)
        return obj

    @classmethod
    def replace(cls, operations, target, replaces = None, replaceWith = None):
        if replaces:
            oldObject = cls._get_object_from_version(operations, replaces)
            dropOld = cls(oldObject).reverse()
            createNew = cls(target)
        elif replaceWith:
            oldObject = cls._get_object_from_version(operations, replaceWith)
            dropOld = cls(target).reverse()
            createNew = cls(oldObject)
        else:
            raise TypeError("replaces or replaceWith is required")

        operations.invoke(dropOld)
        operations.invoke(createNew)

@Operations.register_operation("createStoredProcedure", "invokeForTarget")
@Operations.register_operation("replaceStoredProcedure", "replace")
class CreateStoredProcedureOperation(ReversibleOperation):
    def reverse(self):
        return DropStoredProcedureOperation(self.target)

@Operations.register_operation("dropStoredProcedure", "invokeForTarget")
class DropStoredProcedureOperation(ReversibleOperation):
    def reverse(self):
        return CreateStoredProcedureOperation(self.target)

@Operations.implementation_for(CreateStoredProcedureOperation)
def createStoredProcedure(operations, operation):
    operations.execute("CREATE PROCEDURE %s(%s) %s" % (operation.target.name, operation.target.parameters, operation.target.sqlText))

@Operations.implementation_for(DropStoredProcedureOperation)
def dropStoredProcedure(operations, operation):
    operations.execute("DROP PROCEDURE %s" % operation.target.name)

@Operations.register_operation("createFunction", "invokeForTarget")
@Operations.register_operation("replaceFunction", "replace")
class CreateFunctionOperation(ReversibleOperation):
    def reverse(self):
        return DropFunctionOperation(self.target)

@Operations.register_operation("dropFunction", "invokeForTarget")
class DropFunctionOperation(ReversibleOperation):
    def reverse(self):
        return CreateFunctionOperation(self.target)

@Operations.implementation_for(CreateFunctionOperation)
def createFunction(operations, operation):
    operations.execute("CREATE FUNCTION %s(%s) RETURNS %s %s" % (operation.target.name, operation.target.parameters, operation.target.returns,
        operation.target.sqlText))

@Operations.implementation_for(DropFunctionOperation)
def dropFunction(operations, operation):
    operations.execute("DROP FUNCTION %s" % operation.target.name)
