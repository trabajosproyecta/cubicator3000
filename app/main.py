import os
from flask import Flask, request, redirect, url_for, send_from_directory, flash, render_template
from werkzeug.utils import secure_filename
from cubicator import start
import zipfile

ALLOWED_EXTENSIONS = set(['xlsx', 'xls'])

app = Flask(__name__)
app.secret_key = '1298389172jiklaf83276'

# TODO make this work with non root paths, they most likely have to be created by docker on build
app.config['UPLOAD_FOLDER'] = './'
app.config['RESULTS_FOLDER'] = './'
app.config['IMAGES_FOLDER'] = './'
app.config['ZIPS_FOLDER'] = './'


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No subiste ningún archivo!')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit a empty part without filename
        if file.filename == '':
            flash('No subiste ningún archivo!')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filename_clean, file_ext = os.path.splitext(filename)
            path_file = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(path_file)

            # now we call the optimization start and save the results on the respective folders.
            path_result = os.path.join(app.config['RESULTS_FOLDER'], "result_{}".format(filename_clean))
            path_images = os.path.join(app.config['IMAGES_FOLDER'], "images_{}".format(filename_clean))
            os.makedirs(path_images)
            start(path_file, path_result, path_images + "/")

            # After optimization is over we add the results to zipfile.
            zip_path = os.path.join(app.config['ZIPS_FOLDER'], "zip_{}.zip".format(filename_clean))

            with zipfile.ZipFile(zip_path, "w") as zip:
                zip.write(path_result)
                zip.write(path_result + ".xls")
                for file in os.listdir(path_images):
                    zip.write(os.path.join(path_images, file))

            # TODO Cleanup
            return redirect(url_for('uploaded_file',
                                    filename=filename_clean))
        else:
            flash('Archivo inválido, debes subir un .xlsx o .xls')
            return redirect(request.url)

    return render_template('index.html', error=None)


@app.route('/optimized/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['ZIPS_FOLDER'],
                               "zip {}.zip".format(filename))


if __name__ == "__main__":
    # Only for debugging while developing
    app.run(host='0.0.0.0', debug=True, port=80)
