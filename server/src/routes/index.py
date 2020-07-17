from flask import Blueprint, render_template

index = Blueprint('index', __name__)


@index.route('/', methods=['GET'])
def index_template():
    return render_template('index.html')
