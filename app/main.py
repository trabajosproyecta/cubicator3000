import os
from shutil import rmtree
from flask import Flask, request, redirect, url_for, send_from_directory, flash, render_template, after_this_request
from werkzeug.utils import secure_filename
from cubicator import start
import zipfile

ALLOWED_EXTENSIONS = set(['xlsx', 'xls'])

app = Flask(__name__)
app.secret_key = '1298389172jiklaf83276'

app.config['UPLOAD_FOLDER'] = './temp/images/'
app.config['RESULTS_FOLDER'] = './temp/results/'
app.config['IMAGES_FOLDER'] = './temp/images/'
app.config['ZIPS_FOLDER'] = './temp/zips/'


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
            result_in_dir = "resultado_{}".format(filename_clean)
            images_in_dir = "imagenes_{}".format(filename_clean)
            zips_in_dir = "cubicacion_{}.zip".format(filename_clean)
            path_result = os.path.join(app.config['RESULTS_FOLDER'], result_in_dir)
            path_images = os.path.join(app.config['IMAGES_FOLDER'], images_in_dir)
            os.makedirs(path_images)
            start(path_file, path_result, path_images + "/")

            # After optimization is over we add the results to zipfile.
            zip_path = os.path.join(app.config['ZIPS_FOLDER'], zips_in_dir)

            with zipfile.ZipFile(zip_path, "w") as zip:
                zip.write(path_result,result_in_dir)
                zip.write(path_result + ".xls",result_in_dir + ".xls")
                for file in os.listdir(path_images):
                    zip.write(os.path.join(path_images, file),os.path.join(images_in_dir, file))

            #we clean up intermediary files
            os.remove(path_result)
            os.remove(path_result + '.xls')
            rmtree(path_images)
            os.remove(path_file)



            return redirect(url_for('uploaded_file',
                                    filename=filename_clean))
        else:
            flash('Archivo inválido, debes subir un .xlsx o .xls')
            return redirect(request.url)

    return render_template('index.html', error=None)


@app.route('/optimized/<filename>')
def uploaded_file(filename):
    #we cleanup zip after download, only works in linux systems
    @after_this_request
    def remove_zip(response):
        os.remove(os.path.join(app.config['ZIPS_FOLDER'],
                               "cubicacion_{}.zip".format(filename)))
        return response

    return send_from_directory(app.config['ZIPS_FOLDER'],
                               "cubicacion_{}.zip".format(filename))


if __name__ == "__main__":
    # Only for debugging while developing
    app.run(host='0.0.0.0', debug=True, port=80)
