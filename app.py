import os
if os.path.exists("env.py"):
    import env
from flask import Flask, render_template, redirect, request, url_for
from flask_pymongo import PyMongo
# bson.objectid to convert the ID that's been passed across from our template into a readable format that's acceptable by MongoDB.
from bson.objectid import ObjectId

app = Flask(__name__)

app.config["MONGO_URI"] = os.environ.get("MONGO_URI")
app.config["MONGO_DBNAME"] = 'task_manager'

mongo = PyMongo(app)


@app.route('/')
@app.route('/get_tasks')
def get_tasks():
    # tasks collection, which will be returned from making a call directly to Mongo.
    return render_template("tasks.html", tasks=mongo.db.tasks.find())


@app.route('/add_task')
def add_task():
    return render_template("addtask.html", categories=mongo.db.categories.find())


@app.route('/insert_task', methods=['POST'])
def insert_task():
    tasks = mongo.db.tasks  # var to get db from mongo of tasks
    tasks.insert_one(request.form.to_dict())  # send form to dictionary
    # go to the task.html after sending form
    return redirect(url_for('get_tasks'))


@app.route('/edit_task/<task_id>')
def edit_task(task_id):
    # we're fetching the task that matches this task ID
    the_task = mongo.db.tasks.find_one({"_id": ObjectId(task_id)})
    # The second thing we need is a list of the collections because we're going to use the task that's returned from MongoDB and all the categories in order to populate a form for editing.
    all_categories = mongo.db.categories.find()
    return render_template('edittask.html', task=the_task, categories=all_categories)


@app.route('/update_task/<task_id>', methods=["POST"])
# We pass in the task ID because that's our hook into the primary key.
def update_task(task_id):
    tasks = mongo.db.tasks
    """ So what we do is we access the tasks collection.
    Then we call the update function.We specify the ID.
    That's our key to uniqueness."""
    tasks.update({'_id': ObjectId(task_id)},
                 {
        'task_name': request.form.get('task_name'),
        'category_name': request.form.get('category_name'),
        'task_description': request.form.get('task_description'),
        'due_date': request.form.get('due_date'),
        'is_urgent': request.form.get('is_urgent')
    })
    return redirect(url_for('get_tasks'))


@app.route('/delete_task/<task_id>')
def delete_task(task_id):
    mongo.db.tasks.remove({'_id': ObjectId(task_id)})
    return redirect(url_for('get_tasks'))


@app.route('/get_categories')
def get_categories():
    return render_template('categories.html',
                           categories=mongo.db.categories.find())  # to do a find on the categories table.


@app.route('/insert_category', methods=['POST'])
def insert_category():
    category_doc = {'category_name': request.form.get(
        'category_name')}  # send form to dictionary
    mongo.db.categories.insert(category_doc)
    return redirect(url_for('get_categories'))


@app.route('/add_category')
def add_category():
    return render_template("addcategory.html")


@app.route('/edit_category/<category_id>')
def edit_category(category_id):
    return render_template('editcategory.html',
                           category=mongo.db.categories.find_one({'_id': ObjectId(category_id)}))  # to do a find on the categories table.


@app.route('/update_category/<category_id>', methods=["POST"])
def update_category(category_id):
    mongo.db.categories.update(
        {'_id': ObjectId(category_id)},
        {'category_name': request.form.get('category_name')})
    return redirect(url_for('get_categories'))


@app.route('/delete_category/<category_id>')
def delete_category(category_id):
    mongo.db.categories.remove({'_id': ObjectId(category_id)})
    return redirect(url_for('get_categories'))


if __name__ == '__main__':
    app.run(host=os.environ.get('IP', '0.0.0.0'),
            port=int(os.environ.get('PORT', '5000')),
            debug=True)
    """
    app.run(host=os.environ.get('IP', '127.0.0.1'),
            port=int(os.environ.get('PORT', '8080')),
            debug=True)
    """
