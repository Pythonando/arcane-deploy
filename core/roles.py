from rolepermissions.roles import AbstractUserRole

class Gerente(AbstractUserRole):
    available_permissions = {
        'treinar_ia': True
    }