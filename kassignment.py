from flask import Flask,jsonify,request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import re

app=Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///test.db'
db=SQLAlchemy(app)

class Contact(db.Model):
    id=db.Column(db.Integer,primary_key=True)  # SERIAL equivalent
    name=db.Column(db.String(50),nullable=False)
    email=db.Column(db.String(100),unique=True, nullable=False)
    phone=db.Column(db.String(10),nullable=False)
    created_at=db.Column(db.DateTime,default=datetime.now)
    updated_at=db.Column(db.DateTime,default=datetime.now,onupdate=datetime.now)


#VALIDATION
def is_valid_email(email):
    return re.match(r"^[\w\.-]+@[\w\.-]+\.\w+$",email)

def is_valid_phone(phone):
    return phone.isdigit() and len(phone)==10


#CREATE
@app.route('/api/contacts',methods=['POST'])
def create_contact():
    data=request.json
    if not data.get('name') or not data.get('email') or not data.get('phone'):
        return jsonify({"error": "Missing required fields"}),400
    
    if Contact.query.filter_by(email=data['email']).first():
        return jsonify({"error": "Email already exists"}),400
    
    if not is_valid_phone(data['phone']):
        return jsonify({"error":"Phone must be digits only and 10 characters"}),400

    if not is_valid_email(data['email']):
        return jsonify({"error": "Invalid email format"}),400



    contact=Contact(
        name=data['name'],
        email=data['email'],
        phone=data['phone']
    )
    db.session.add(contact)
    db.session.commit()
    return jsonify({"message":"Contact created","id":contact.id}),201

#READ
@app.route('/api/contacts',methods=['GET'])
def get_contacts():
    contacts=Contact.query.all()
    return jsonify([{
        "id":c.id,
        "name":c.name,
        "email":c.email,
        "phone":c.phone} for c in contacts])

#UPDATE
@app.route('/api/contacts/<int:id>',methods=['PUT'])
def update_contact(id):
    contact=Contact.query.get_or_404(id)
    data=request.json

    if 'email' in data and not is_valid_email(data['email']):
        return jsonify({"error":"Invalid email format"}),400

    if 'phone' in data and not is_valid_phone(data['phone']):
        return jsonify({"error": "Phone must be digits only and 10 characters"}),400


    contact.name=data.get('name', contact.name)
    contact.email=data.get('email', contact.email)
    contact.phone=data.get('phone', contact.phone)
    db.session.commit()
    return jsonify({"message":"Contact updated"})

# DELETE
@app.route('/api/contacts/<int:id>',methods=['DELETE'])
def delete_contact(id):
    contact=Contact.query.get_or_404(id)
    db.session.delete(contact)
    db.session.commit()
    return jsonify({"message":"Contact deleted"})





#MAIN
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
