from tortoise import migrations
from tortoise.migrations import operations as ops
from app.accidents.value_sets import AircraftDamage, FlightSchedule, InvestigationType, ReportStatus, Severity, WeatherCondition
from tortoise.fields.base import OnDelete
from tortoise import fields
from tortoise.indexes import Index

class Migration(migrations.Migration):
    initial = True

    operations = [
        ops.CreateModel(
            name='AircraftCategory',
            fields=[
                ('id', fields.IntField(generated=True, primary_key=True, unique=True, db_index=True)),
                ('name', fields.CharField(unique=True, max_length=128)),
            ],
            options={'table': 'aircraft_category', 'app': 'models', 'pk_attr': 'id'},
            bases=['LookupBase'],
        ),
        ops.CreateModel(
            name='Country',
            fields=[
                ('id', fields.IntField(generated=True, primary_key=True, unique=True, db_index=True)),
                ('name', fields.CharField(unique=True, max_length=128)),
            ],
            options={'table': 'country', 'app': 'models', 'pk_attr': 'id'},
            bases=['LookupBase'],
        ),
        ops.CreateModel(
            name='EngineType',
            fields=[
                ('id', fields.IntField(generated=True, primary_key=True, unique=True, db_index=True)),
                ('name', fields.CharField(unique=True, max_length=128)),
            ],
            options={'table': 'engine_type', 'app': 'models', 'pk_attr': 'id'},
            bases=['LookupBase'],
        ),
        ops.CreateModel(
            name='Event',
            fields=[
                ('id', fields.IntField(generated=True, primary_key=True, unique=True, db_index=True)),
                ('event_id', fields.CharField(unique=True, max_length=32)),
                ('event_date', fields.DateField(db_index=True)),
                ('event_year', fields.SmallIntField(db_index=True)),
                ('location', fields.CharField(null=True, max_length=128)),
                ('country', fields.ForeignKeyField('models.Country', source_field='country_id', null=True, db_constraint=True, to_field='id', related_name='events', on_delete=OnDelete.SET_NULL)),
                ('latitude', fields.FloatField(null=True)),
                ('longitude', fields.FloatField(null=True)),
                ('airport_code', fields.CharField(null=True, max_length=16)),
                ('airport_name', fields.CharField(null=True, max_length=128)),
                ('weather_condition', fields.CharEnumField(null=True, description='VMC: VMC\nIMC: IMC\nUNK: UNK', enum_type=WeatherCondition, max_length=3)),
                ('investigation_type', fields.CharEnumField(description='ACCIDENT: Accident\nINCIDENT: Incident', enum_type=InvestigationType, max_length=8)),
                ('report_status', fields.CharEnumField(null=True, description='PROBABLE_CAUSE: Probable Cause\nFACTUAL: Factual\nPRELIMINARY: Preliminary\nFOREIGN: Foreign', enum_type=ReportStatus, max_length=14)),
                ('publication_date', fields.DateField(null=True)),
                ('max_severity', fields.CharEnumField(null=True, description='FATAL: Fatal\nNON_FATAL: Non-Fatal\nINCIDENT: Incident\nUNAVAILABLE: Unavailable', enum_type=Severity, max_length=11)),
            ],
            options={'table': 'event', 'app': 'models', 'indexes': [Index(fields=['event_year', 'latitude', 'longitude'])], 'pk_attr': 'id'},
            bases=['Model'],
        ),
        ops.CreateModel(
            name='FarDescription',
            fields=[
                ('id', fields.IntField(generated=True, primary_key=True, unique=True, db_index=True)),
                ('name', fields.CharField(unique=True, max_length=128)),
            ],
            options={'table': 'far_description', 'app': 'models', 'pk_attr': 'id'},
            bases=['LookupBase'],
        ),
        ops.CreateModel(
            name='FlightPhase',
            fields=[
                ('id', fields.IntField(generated=True, primary_key=True, unique=True, db_index=True)),
                ('name', fields.CharField(unique=True, max_length=128)),
            ],
            options={'table': 'flight_phase', 'app': 'models', 'pk_attr': 'id'},
            bases=['LookupBase'],
        ),
        ops.CreateModel(
            name='FlightPurpose',
            fields=[
                ('id', fields.IntField(generated=True, primary_key=True, unique=True, db_index=True)),
                ('name', fields.CharField(unique=True, max_length=128)),
            ],
            options={'table': 'flight_purpose', 'app': 'models', 'pk_attr': 'id'},
            bases=['LookupBase'],
        ),
        ops.CreateModel(
            name='Manufacturer',
            fields=[
                ('id', fields.IntField(generated=True, primary_key=True, unique=True, db_index=True)),
                ('name', fields.CharField(unique=True, max_length=128)),
            ],
            options={'table': 'manufacturer', 'app': 'models', 'pk_attr': 'id'},
            bases=['Model'],
        ),
        ops.CreateModel(
            name='Aircraft',
            fields=[
                ('id', fields.IntField(generated=True, primary_key=True, unique=True, db_index=True)),
                ('accident_number', fields.CharField(unique=True, max_length=32)),
                ('event', fields.ForeignKeyField('models.Event', source_field='event_id', db_constraint=True, to_field='id', related_name='aircraft', on_delete=OnDelete.CASCADE)),
                ('registration_number', fields.CharField(null=True, max_length=32)),
                ('manufacturer', fields.ForeignKeyField('models.Manufacturer', source_field='manufacturer_id', null=True, db_constraint=True, to_field='id', related_name='aircraft', on_delete=OnDelete.SET_NULL)),
                ('model', fields.CharField(null=True, max_length=64)),
                ('category', fields.ForeignKeyField('models.AircraftCategory', source_field='category_id', null=True, db_constraint=True, to_field='id', related_name='aircraft', on_delete=OnDelete.SET_NULL)),
                ('amateur_built', fields.BooleanField(null=True)),
                ('number_of_engines', fields.SmallIntField(null=True)),
                ('engine_type', fields.ForeignKeyField('models.EngineType', source_field='engine_type_id', null=True, db_constraint=True, to_field='id', related_name='aircraft', on_delete=OnDelete.SET_NULL)),
                ('far_description', fields.ForeignKeyField('models.FarDescription', source_field='far_description_id', null=True, db_constraint=True, to_field='id', related_name='aircraft', on_delete=OnDelete.SET_NULL)),
                ('schedule', fields.CharEnumField(null=True, description='SCHEDULED: SCHD\nNON_SCHEDULED: NSCH\nUNKNOWN: UNK', enum_type=FlightSchedule, max_length=4)),
                ('purpose', fields.ForeignKeyField('models.FlightPurpose', source_field='purpose_id', null=True, db_constraint=True, to_field='id', related_name='aircraft', on_delete=OnDelete.SET_NULL)),
                ('air_carrier', fields.CharField(null=True, max_length=256)),
                ('broad_phase_of_flight', fields.ForeignKeyField('models.FlightPhase', source_field='broad_phase_of_flight_id', null=True, db_constraint=True, to_field='id', related_name='aircraft', on_delete=OnDelete.SET_NULL)),
                ('aircraft_damage', fields.CharEnumField(null=True, description='DESTROYED: Destroyed\nSUBSTANTIAL: Substantial\nMINOR: Minor', enum_type=AircraftDamage, max_length=11)),
                ('severity', fields.CharEnumField(null=True, description='FATAL: Fatal\nNON_FATAL: Non-Fatal\nINCIDENT: Incident\nUNAVAILABLE: Unavailable', enum_type=Severity, max_length=11)),
                ('fatal_injuries', fields.SmallIntField(null=True)),
                ('serious_injuries', fields.SmallIntField(null=True)),
                ('minor_injuries', fields.SmallIntField(null=True)),
                ('uninjured', fields.SmallIntField(null=True)),
            ],
            options={'table': 'aircraft', 'app': 'models', 'pk_attr': 'id'},
            bases=['Model'],
        ),
    ]
