# lambu_login

## Descripción:

Este módulo está diseñado para gestionar el control de acceso al sistema
permitiendo el mantenimiento de permisos de usuarios del ámbito de la empresa.

## Instalación:

Instalación común de un modúlo de Odoo.

## Funcionalidades:

- Mantenimiento de usuarios lambu.
- Visualización de sesiones.
- Autentificación del usuario lambu.

## Limitaciones

- Las permisologías del usuario lambu son heredadas del usuario Odoo y por
 ende sus permisos no se pueden modificar. 
- La trazabilidad de las operaciones de Odoo se siguen llevando por el usuario Odoo.

## Historias de usuario


## Consideraciones

En cuento a las funcionalidades realizadas en el login  existe la posibilidad que se vea afectado
el flujo comun de Odoo en tema de la duracion de sesiones, log de usuarios.
