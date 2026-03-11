import sys
sys.path.insert(0,'backend')
from run import app, db, Officer, ValidOfficer, Worker, User

with app.app_context():
    # recreate schema
    db.drop_all()
    db.create_all()
    from run import init_seed_data, create_default_workers, create_default_officers
    init_seed_data()
    create_default_workers()
    create_default_officers()
    print('='*60)
    print('[DATABASE DEBUG] Current database state:')
    print('  - Citizens registered:', db.session.query(User).filter_by(role='citizen').count())
    print('  - Officers registered:', db.session.query(User).filter_by(role='officer').count())
    print('  - Admin users:', db.session.query(User).filter_by(role='admin').count())
    print('  - Valid officers (pre-approved IDs):', ValidOfficer.query.count())
    print('  - Workers:', Worker.query.count())
    print('  - Default officers:', Officer.query.count())
    print('='*60)
    print('Default officers list:')
    for o in Officer.query.all():
        print(' -', o.email, o.name, o.department, o.password)
