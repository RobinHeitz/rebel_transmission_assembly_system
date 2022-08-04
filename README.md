# rebel_transmission_assembly_system

This repo serves as an assembly aid for Rebel gearboxes. 'PySimpleGUI' is used as frontend, 'python-can' is used as driver for the PeakCAN USB Interface.
For data saving SQLAlchemy is used as ORM-Tool (Object Relational Mapping) and sqlite as database.
Alembic is a tool for database setup/ migration (change tables etc.).

use 'python start_app.py' in console to start GUI interface.

## Prerequisite:
- Install PeakCAN Driver for windows
- use the following 'CAN to USB interface': https://www.peak-system.com/PCAN-USB.199.0.html?&L=1
- Install all needed packages with pip: pip install -r -y requirements.txt

## Structure of this repository
- /alembic is stuff for database migration. You might not touch it.
- /data_management defines data models, managed with SQLAlchemy
- /hw_interface is the implementation for connecting/ controlling the ReBeL Gearbox. 
- /gui is stuff related to the gui (PySimpleGUI)
- /testing_stuff for scripts testing single components before they got implemented in the gui-app

### hw_interface.motor_controller.py
- use class 'RebelAxisController' for connecting/ controlling rebel gear. After init, call method start_msg_listener_thread(). A thread is started which reads every message the BLDC-Board is sending. Access to this messages with properties 'movement_cmd_reply_list' (replies for movement commands; instances of MessageMovementCommandReply) and 'motor_env_status_list' (Non-cyclical environment status messages; instances of class MessageEnvironmentStatus)


### Using alembic auto-migration:
alembic revision --autogenerate -m "my migration description" 
alembic upgrade head