# rebel_transmission_assembly_system

## Prerequisite:
- Install PeakCAN Driver for windows
- use the following 'CAN to USB interface': https://www.peak-system.com/PCAN-USB.199.0.html?&L=1



## Database: SQAlchemy 
### Using alembic auto-migration:
alembic revision --autogenerate -m "my migration description" 
alembic upgrade head