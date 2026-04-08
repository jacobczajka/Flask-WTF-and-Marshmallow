from flask import Flask, render_template, request, jsonify
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, SubmitField
from wtforms.validators import DataRequired, Email, Length
from marshmallow import Schema, fields, validate, ValidationError

app = Flask(__name__)
app.config['SECRET_KEY'] = 'super-tajne-haslo-prezentacyjne'

# --- FLASK-WTF: Formularz kontaktowy z różnymi typami pól ---
class TicketForm(FlaskForm):
    subject = StringField('Temat zgłoszenia', validators=[
        DataRequired(message="Podaj temat"),
        Length(min=5, message="Temat musi mieć min. 5 znaków")
    ])
    email = StringField('Twój Email', validators=[DataRequired(), Email()])
    priority = SelectField('Priorytet', choices=[
        ('low', 'Niski'), ('medium', 'Średni'), ('high', 'Wysoki')
    ])
    message = TextAreaField('Treść', validators=[DataRequired()])
    submit = SubmitField('Wyślij zgłoszenie (SSR)')

# --- MARSHMALLOW: Schemat API z zaawansowaną walidacją ---
class ProductSchema(Schema):
    name = fields.Str(required=True, validate=validate.Length(min=2, max=50))
    price = fields.Float(required=True, validate=validate.Range(min=0.01, error="Cena musi być dodatnia"))
    category = fields.Str(required=True, validate=validate.OneOf(["Elektronika", "Dom", "Ogród"]))
    tags = fields.List(fields.Str(), validate=validate.Length(max=3))

@app.route('/', methods=['GET', 'POST'])
def index():
    form = TicketForm()
    success_msg = None
    if form.validate_on_submit():
        success_msg = f"Otrzymano zgłoszenie: {form.subject.data}"
    return render_template('index.html', form=form, success_msg=success_msg)

@app.route('/api/validate', methods=['POST'])
def api_validate():
    json_data = request.get_json()
    schema = ProductSchema()
    try:
        data = schema.load(json_data)
        return jsonify({"status": "Success", "validated_data": data}), 200
    except ValidationError as err:
        return jsonify({"status": "Invalid Data", "errors": err.messages}), 400

if __name__ == '__main__':
    app.run(debug=True)
