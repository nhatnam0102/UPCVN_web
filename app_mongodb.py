import os
from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    g,
    flash,
    abort,
    jsonify,
    session,
)
from flask_login import (
    LoginManager,
    current_user,
    login_user,
    logout_user,
    login_required,
    UserMixin,
)
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import json
from pymongo import MongoClient
from bson.objectid import ObjectId

# App setup
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "your-secret-key")
app.config["UPLOAD_FOLDER"] = "static/images/uploads"
app.config["ALLOWED_EXTENSIONS"] = {"png", "jpg", "jpeg", "gif"}

# Setup MongoDB connection
mongo_client = MongoClient(os.environ.get("MONGODB_URI", "mongodb://localhost:27017"))
db = mongo_client.get_database(os.environ.get("MONGODB_DB_NAME", "upcvn"))

# Initialize LoginManager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"
login_manager.login_message = "Vui lòng đăng nhập để truy cập trang này."


# User class for Flask-Login
class User(UserMixin):
    def __init__(self, user_data):
        self.id = str(user_data["_id"])
        self.username = user_data["username"]
        self.email = user_data["email"]
        self.password_hash = user_data["password_hash"]
        self.is_admin = user_data.get("is_admin", False)
        self.created_at = user_data.get("created_at", datetime.utcnow())

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @staticmethod
    def get_by_id(user_id):
        user_data = db.users.find_one({"_id": ObjectId(user_id)})
        if not user_data:
            return None
        return User(user_data)

    @staticmethod
    def get_by_username(username):
        user_data = db.users.find_one({"username": username})
        if not user_data:
            return None
        return User(user_data)


@login_manager.user_loader
def load_user(user_id):
    return User.get_by_id(user_id)


# Language and translation setup
@app.before_request
def before_request():
    g.language = request.cookies.get("language", "vi")

    if g.language == "vi":
        from translations.vi import translations
    else:
        from translations.ja import translations

    g.translations = translations


@app.route("/change-language/<language>")
def change_language(language):
    response = redirect(request.referrer or url_for("index"))
    response.set_cookie("language", language)
    return response


# Helper functions
def allowed_file(filename):
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in app.config["ALLOWED_EXTENSIONS"]
    )


def save_uploaded_file(file, folder="uploads"):
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        # Add timestamp to filename to avoid duplicates
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        new_filename = f"{timestamp}_{filename}"

        # Create folder if it doesn't exist
        folder_path = os.path.join(app.config["UPLOAD_FOLDER"], folder)
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

        file_path = os.path.join(folder_path, new_filename)
        file.save(file_path)
        return f"images/uploads/{folder}/{new_filename}"
    return None


# Initialize database with content from current HTML
def import_content_from_html():
    # Check if we already have data
    if db.products.count_documents({}) > 0:
        return

    # Import products from translations
    products = [
        {
            "title_vi": "BT Cloud",
            "title_ja": "BTクラウド",
            "description_vi": "Giải pháp quản lý doanh nghiệp toàn diện trên nền tảng điện toán đám mây.",
            "description_ja": "クラウドベースの包括的なビジネス管理ソリューション。",
            "image": "images/products/bt_cloud.jpg",
            "order": 1,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        },
        {
            "title_vi": "Giải pháp AI",
            "title_ja": "AIソリューション",
            "description_vi": "Ứng dụng trí tuệ nhân tạo vào quy trình sản xuất và kiểm soát chất lượng.",
            "description_ja": "製造工程と品質管理への人工知能の応用。",
            "image": "images/products/ai.jpg",
            "order": 2,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        },
        {
            "title_vi": "WMS Cloud",
            "title_ja": "WMSクラウド",
            "description_vi": "Hệ thống quản lý kho hàng thông minh với khả năng tích hợp IoT.",
            "description_ja": "IoT統合機能を備えたスマート倉庫管理システム。",
            "image": "images/products/wms.jpg",
            "order": 3,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        },
        {
            "title_vi": "IoT Collector",
            "title_ja": "IoTコレクター",
            "description_vi": "Thu thập và phân tích dữ liệu từ các thiết bị IoT trong môi trường sản xuất.",
            "description_ja": "製造環境におけるIoTデバイスからのデータ収集と分析。",
            "image": "images/products/iot.jpg",
            "order": 4,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        },
        {
            "title_vi": "Cybouz Garoon & Kintone",
            "title_ja": "サイボウズ ガルーン & kintone",
            "description_vi": "Tích hợp và tùy chỉnh nền tảng Cybouz cho doanh nghiệp Nhật Bản.",
            "description_ja": "日本企業向けサイボウズプラットフォームの統合とカスタマイズ。",
            "image": "images/products/cybouz.jpg",
            "order": 5,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        },
        {
            "title_vi": "Giải pháp tùy chỉnh",
            "title_ja": "カスタムソリューション",
            "description_vi": "Phát triển các giải pháp phần mềm tùy chỉnh theo yêu cầu của doanh nghiệp.",
            "description_ja": "ビジネスニーズに合わせたカスタムソフトウェアソリューションの開発。",
            "image": "images/products/custom.jpg",
            "order": 6,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        },
    ]

    db.products.insert_many(products)

    # Import case studies
    case_studies = [
        {
            "title_vi": "Tích hợp Kintone",
            "title_ja": "kintone統合",
            "description_vi": "Tích hợp nền tảng kintone với các hệ thống nội bộ của doanh nghiệp.",
            "description_ja": "kintoneプラットフォームと企業の内部システムの統合。",
            "category_vi": "Tích hợp",
            "category_ja": "統合",
            "image": "images/case_studies/case_kintone.jpg",
            "order": 1,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        },
        {
            "title_vi": "Kiểm tra AI",
            "title_ja": "AI検査",
            "description_vi": "Hệ thống kiểm tra chất lượng tự động sử dụng trí tuệ nhân tạo.",
            "description_ja": "人工知能を使用した自動品質検査システム。",
            "category_vi": "Công nghệ AI",
            "category_ja": "AI技術",
            "image": "images/case_studies/case_ai_inspection.jpg",
            "order": 2,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        },
        {
            "title_vi": "Quản lý lao động nước ngoài",
            "title_ja": "外国人労働者管理",
            "description_vi": "Hệ thống quản lý lao động nước ngoài toàn diện.",
            "description_ja": "包括的な外国人労働者管理システム。",
            "category_vi": "Quản lý",
            "category_ja": "管理",
            "image": "images/case_studies/case_foreign_labor.jpg",
            "order": 3,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        },
        {
            "title_vi": "AI-OCR",
            "title_ja": "AI-OCR",
            "description_vi": "Giải pháp nhận dạng ký tự quang học thông minh sử dụng AI.",
            "description_ja": "AIを使用したインテリジェントな光学式文字認識ソリューション。",
            "category_vi": "Công nghệ OCR",
            "category_ja": "OCR技術",
            "image": "images/case_studies/case_ai_ocr.jpg",
            "order": 4,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        },
        {
            "title_vi": "Giám sát nhiệt độ",
            "title_ja": "温度モニタリング",
            "description_vi": "Hệ thống giám sát nhiệt độ từ xa cho các thiết bị công nghiệp.",
            "description_ja": "産業機器用の遠隔温度監視システム。",
            "category_vi": "Giám sát",
            "category_ja": "モニタリング",
            "image": "images/case_studies/case_temperature.jpg",
            "order": 5,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        },
        {
            "title_vi": "Thêm dự án",
            "title_ja": "その他のケース",
            "description_vi": "Khám phá thêm nhiều dự án thành công khác của chúng tôi.",
            "description_ja": "当社のその他の成功事例をご覧ください。",
            "category_vi": "Khác",
            "category_ja": "その他",
            "image": "images/case_studies/case_more.jpg",
            "order": 6,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        },
    ]

    db.case_studies.insert_many(case_studies)

    # Import news
    news = [
        {
            "title_vi": "Khai trương văn phòng mới",
            "title_ja": "新オフィスオープン",
            "description_vi": "U-Mate khai trương văn phòng mới tại Hà Nội, mở rộng hoạt động kinh doanh.",
            "description_ja": "U-Mateがハノイに新オフィスをオープンし、事業を拡大。",
            "content_vi": "Chi tiết về khai trương văn phòng mới của U-Mate tại Hà Nội.",
            "content_ja": "ハノイにおけるU-Mateの新オフィスオープンについての詳細。",
            "date": datetime(
                2025, 1, 15
            ),  # Use datetime.datetime instead of datetime.date
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        },
        {
            "title_vi": "Hợp tác với Microsoft",
            "title_ja": "マイクロソフトとの提携",
            "description_vi": "U-Mate trở thành đối tác chính thức của Microsoft tại Việt Nam.",
            "description_ja": "U-Mateがベトナムにおけるマイクロソフトの正式パートナーに。",
            "content_vi": "Chi tiết về hợp tác với Microsoft của U-Mate.",
            "content_ja": "U-Mateとマイクロソフトとのパートナーシップについての詳細。",
            "date": datetime(
                2025, 2, 20
            ),  # Use datetime.datetime instead of datetime.date
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        },
        {
            "title_vi": "Ra mắt sản phẩm mới",
            "title_ja": "新製品発表",
            "description_vi": "U-Mate ra mắt giải pháp AI mới cho ngành sản xuất.",
            "description_ja": "U-Mateが製造業向け新AIソリューションを発表。",
            "content_vi": "Chi tiết về sản phẩm AI mới của U-Mate.",
            "content_ja": "U-Mateの新しいAIソリューションについての詳細。",
            "date": datetime(
                2025, 3, 10
            ),  # Use datetime.datetime instead of datetime.date
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        },
    ]

    db.news.insert_many(news)

    # Create default admin user if not exists
    if db.users.count_documents({"is_admin": True}) == 0:
        admin_user = {
            "username": "admin",
            "email": "admin@example.com",
            "password_hash": generate_password_hash("admin123"),
            "is_admin": True,
            "created_at": datetime.utcnow(),
        }
        db.users.insert_one(admin_user)


# Public routes
@app.route("/")
def index():
    # Get products and case studies from MongoDB
    products = list(db.products.find().sort("order", 1))
    case_studies = list(db.case_studies.find().sort("order", 1))
    news_items = list(db.news.find().sort("date", -1).limit(3))

    return render_template(
        "index_mongodb.html",
        products=products,
        case_studies=case_studies,
        news=news_items,
    )


@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        # Process form submission
        name = request.form.get("name")
        email = request.form.get("email")
        phone = request.form.get("phone")
        company = request.form.get("company")
        subject = request.form.get("subject")
        message = request.form.get("message")

        if name and email and subject and message:
            contact_data = {
                "name": name,
                "email": email,
                "phone": phone,
                "company": company,
                "subject": subject,
                "message": message,
                "is_read": False,
                "created_at": datetime.utcnow(),
            }

            db.contacts.insert_one(contact_data)
            return render_template("contact_success.html")
        else:
            flash("Vui lòng điền đầy đủ thông tin bắt buộc.", "danger")

    return render_template("contact.html")


# Admin authentication routes
@app.route("/admin/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("admin_dashboard"))

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        user = User.get_by_username(username)

        if user and user.check_password(password):
            login_user(user)
            next_page = request.args.get("next")
            return redirect(next_page or url_for("admin_dashboard"))
        else:
            flash("Tên đăng nhập hoặc mật khẩu không đúng", "danger")

    return render_template("admin/login.html")


@app.route("/admin/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))


# Admin routes
@app.route("/admin")
@login_required
def admin_dashboard():
    if not current_user.is_admin:
        abort(403)

    # Count items for dashboard
    products_count = db.products.count_documents({})
    case_studies_count = db.case_studies.count_documents({})
    news_count = db.news.count_documents({})
    contacts_count = db.contacts.count_documents({})
    unread_contacts = db.contacts.count_documents({"is_read": False})

    return render_template(
        "admin/dashboard.html",
        products_count=products_count,
        case_studies_count=case_studies_count,
        news_count=news_count,
        contacts_count=contacts_count,
        unread_contacts=unread_contacts,
    )


# Products admin routes
@app.route("/admin/products")
@login_required
def admin_products():
    if not current_user.is_admin:
        abort(403)

    products = list(db.products.find().sort("order", 1))
    return render_template("admin/products/index.html", products=products)


@app.route("/admin/products/create", methods=["GET", "POST"])
@login_required
def admin_products_create():
    if not current_user.is_admin:
        abort(403)

    if request.method == "POST":
        title_vi = request.form.get("title_vi")
        title_ja = request.form.get("title_ja")
        description_vi = request.form.get("description_vi")
        description_ja = request.form.get("description_ja")
        order = int(request.form.get("order", 0))

        # Handle image upload
        image = request.files.get("image")
        image_path = save_uploaded_file(image, "products")

        if title_vi and title_ja and description_vi and description_ja and image_path:
            product_data = {
                "title_vi": title_vi,
                "title_ja": title_ja,
                "description_vi": description_vi,
                "description_ja": description_ja,
                "image": image_path,
                "order": order,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
            }

            db.products.insert_one(product_data)
            flash("Sản phẩm đã được tạo thành công", "success")
            return redirect(url_for("admin_products"))
        else:
            flash("Vui lòng điền đầy đủ thông tin bắt buộc", "danger")

    return render_template("admin/products/create.html")


@app.route("/admin/products/edit/<product_id>", methods=["GET", "POST"])
@login_required
def admin_products_edit(product_id):
    if not current_user.is_admin:
        abort(403)

    product = db.products.find_one({"_id": ObjectId(product_id)})
    if not product:
        abort(404)

    if request.method == "POST":
        title_vi = request.form.get("title_vi")
        title_ja = request.form.get("title_ja")
        description_vi = request.form.get("description_vi")
        description_ja = request.form.get("description_ja")
        order = int(request.form.get("order", 0))

        # Update data
        update_data = {
            "title_vi": title_vi,
            "title_ja": title_ja,
            "description_vi": description_vi,
            "description_ja": description_ja,
            "order": order,
            "updated_at": datetime.utcnow(),
        }

        # Handle image upload if new image is provided
        image = request.files.get("image")
        if image and image.filename:
            image_path = save_uploaded_file(image, "products")
            if image_path:
                update_data["image"] = image_path

        db.products.update_one({"_id": ObjectId(product_id)}, {"$set": update_data})
        flash("Sản phẩm đã được cập nhật thành công", "success")
        return redirect(url_for("admin_products"))

    return render_template("admin/products/edit.html", product=product)


@app.route("/admin/products/delete/<product_id>", methods=["POST"])
@login_required
def admin_products_delete(product_id):
    if not current_user.is_admin:
        abort(403)

    product = db.products.find_one({"_id": ObjectId(product_id)})
    if not product:
        abort(404)

    db.products.delete_one({"_id": ObjectId(product_id)})
    flash("Sản phẩm đã được xóa thành công", "success")
    return redirect(url_for("admin_products"))


# Case Studies admin routes
@app.route("/admin/case-studies")
@login_required
def admin_case_studies():
    if not current_user.is_admin:
        abort(403)

    case_studies = list(db.case_studies.find().sort("order", 1))
    return render_template("admin/case_studies/index.html", case_studies=case_studies)


@app.route("/admin/case-studies/create", methods=["GET", "POST"])
@login_required
def admin_case_studies_create():
    if not current_user.is_admin:
        abort(403)

    if request.method == "POST":
        title_vi = request.form.get("title_vi")
        title_ja = request.form.get("title_ja")
        description_vi = request.form.get("description_vi")
        description_ja = request.form.get("description_ja")
        category_vi = request.form.get("category_vi")
        category_ja = request.form.get("category_ja")
        order = int(request.form.get("order", 0))

        # Handle image upload
        image = request.files.get("image")
        image_path = save_uploaded_file(image, "case_studies")

        if (
            title_vi
            and title_ja
            and description_vi
            and description_ja
            and category_vi
            and category_ja
            and image_path
        ):
            case_study_data = {
                "title_vi": title_vi,
                "title_ja": title_ja,
                "description_vi": description_vi,
                "description_ja": description_ja,
                "category_vi": category_vi,
                "category_ja": category_ja,
                "image": image_path,
                "order": order,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
            }

            db.case_studies.insert_one(case_study_data)
            flash("Dự án đã được tạo thành công", "success")
            return redirect(url_for("admin_case_studies"))
        else:
            flash("Vui lòng điền đầy đủ thông tin bắt buộc", "danger")

    return render_template("admin/case_studies/create.html")


@app.route("/admin/case-studies/edit/<case_study_id>", methods=["GET", "POST"])
@login_required
def admin_case_studies_edit(case_study_id):
    if not current_user.is_admin:
        abort(403)

    case_study = db.case_studies.find_one({"_id": ObjectId(case_study_id)})
    if not case_study:
        abort(404)

    if request.method == "POST":
        title_vi = request.form.get("title_vi")
        title_ja = request.form.get("title_ja")
        description_vi = request.form.get("description_vi")
        description_ja = request.form.get("description_ja")
        category_vi = request.form.get("category_vi")
        category_ja = request.form.get("category_ja")
        order = int(request.form.get("order", 0))

        # Update data
        update_data = {
            "title_vi": title_vi,
            "title_ja": title_ja,
            "description_vi": description_vi,
            "description_ja": description_ja,
            "category_vi": category_vi,
            "category_ja": category_ja,
            "order": order,
            "updated_at": datetime.utcnow(),
        }

        # Handle image upload if new image is provided
        image = request.files.get("image")
        if image and image.filename:
            image_path = save_uploaded_file(image, "case_studies")
            if image_path:
                update_data["image"] = image_path

        db.case_studies.update_one(
            {"_id": ObjectId(case_study_id)}, {"$set": update_data}
        )
        flash("Dự án đã được cập nhật thành công", "success")
        return redirect(url_for("admin_case_studies"))

    return render_template("admin/case_studies/edit.html", case_study=case_study)


@app.route("/admin/case-studies/delete/<case_study_id>", methods=["POST"])
@login_required
def admin_case_studies_delete(case_study_id):
    if not current_user.is_admin:
        abort(403)

    case_study = db.case_studies.find_one({"_id": ObjectId(case_study_id)})
    if not case_study:
        abort(404)

    db.case_studies.delete_one({"_id": ObjectId(case_study_id)})
    flash("Dự án đã được xóa thành công", "success")
    return redirect(url_for("admin_case_studies"))


# News admin routes
@app.route("/admin/news")
@login_required
def admin_news():
    if not current_user.is_admin:
        abort(403)

    news = list(db.news.find().sort("date", -1))
    return render_template("admin/news/index.html", news=news)


@app.route("/admin/news/create", methods=["GET", "POST"])
@login_required
def admin_news_create():
    if not current_user.is_admin:
        abort(403)

    if request.method == "POST":
        title_vi = request.form.get("title_vi")
        title_ja = request.form.get("title_ja")
        description_vi = request.form.get("description_vi")
        description_ja = request.form.get("description_ja")
        content_vi = request.form.get("content_vi")
        content_ja = request.form.get("content_ja")
        date_str = request.form.get("date")

        if (
            title_vi
            and title_ja
            and description_vi
            and description_ja
            and content_vi
            and content_ja
            and date_str
        ):
            try:
                date = datetime.strptime(date_str, "%Y-%m-%d").date()
                news_data = {
                    "title_vi": title_vi,
                    "title_ja": title_ja,
                    "description_vi": description_vi,
                    "description_ja": description_ja,
                    "content_vi": content_vi,
                    "content_ja": content_ja,
                    "date": date,
                    "created_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow(),
                }

                db.news.insert_one(news_data)
                flash("Tin tức đã được tạo thành công", "success")
                return redirect(url_for("admin_news"))
            except ValueError:
                flash("Định dạng ngày không hợp lệ", "danger")
        else:
            flash("Vui lòng điền đầy đủ thông tin bắt buộc", "danger")

    return render_template("admin/news/create.html")


@app.route("/admin/news/edit/<news_id>", methods=["GET", "POST"])
@login_required
def admin_news_edit(news_id):
    if not current_user.is_admin:
        abort(403)

    news = db.news.find_one({"_id": ObjectId(news_id)})
    if not news:
        abort(404)

    if request.method == "POST":
        title_vi = request.form.get("title_vi")
        title_ja = request.form.get("title_ja")
        description_vi = request.form.get("description_vi")
        description_ja = request.form.get("description_ja")
        content_vi = request.form.get("content_vi")
        content_ja = request.form.get("content_ja")
        date_str = request.form.get("date")

        try:
            date = datetime.strptime(date_str, "%Y-%m-%d").date()
            update_data = {
                "title_vi": title_vi,
                "title_ja": title_ja,
                "description_vi": description_vi,
                "description_ja": description_ja,
                "content_vi": content_vi,
                "content_ja": content_ja,
                "date": date,
                "updated_at": datetime.utcnow(),
            }

            db.news.update_one({"_id": ObjectId(news_id)}, {"$set": update_data})
            flash("Tin tức đã được cập nhật thành công", "success")
            return redirect(url_for("admin_news"))
        except ValueError:
            flash("Định dạng ngày không hợp lệ", "danger")

    return render_template("admin/news/edit.html", news=news)


@app.route("/admin/news/delete/<news_id>", methods=["POST"])
@login_required
def admin_news_delete(news_id):
    if not current_user.is_admin:
        abort(403)

    news = db.news.find_one({"_id": ObjectId(news_id)})
    if not news:
        abort(404)

    db.news.delete_one({"_id": ObjectId(news_id)})
    flash("Tin tức đã được xóa thành công", "success")
    return redirect(url_for("admin_news"))


# Contact admin routes
@app.route("/admin/contacts")
@login_required
def admin_contacts():
    if not current_user.is_admin:
        abort(403)

    contacts = list(db.contacts.find().sort("created_at", -1))
    return render_template("admin/contacts/index.html", contacts=contacts)


@app.route("/admin/contacts/view/<contact_id>")
@login_required
def admin_contacts_view(contact_id):
    if not current_user.is_admin:
        abort(403)

    contact = db.contacts.find_one({"_id": ObjectId(contact_id)})
    if not contact:
        abort(404)

    # Mark as read if it wasn't already
    if not contact.get("is_read", False):
        db.contacts.update_one(
            {"_id": ObjectId(contact_id)}, {"$set": {"is_read": True}}
        )

    return render_template("admin/contacts/view.html", contact=contact)


@app.route("/admin/contacts/delete/<contact_id>", methods=["POST"])
@login_required
def admin_contacts_delete(contact_id):
    if not current_user.is_admin:
        abort(403)

    contact = db.contacts.find_one({"_id": ObjectId(contact_id)})
    if not contact:
        abort(404)

    db.contacts.delete_one({"_id": ObjectId(contact_id)})
    flash("Liên hệ đã được xóa thành công", "success")
    return redirect(url_for("admin_contacts"))


# Settings admin routes
@app.route("/admin/settings")
@login_required
def admin_settings():
    if not current_user.is_admin:
        abort(403)

    settings = {}
    all_settings = list(db.settings.find())

    for setting in all_settings:
        group = setting.get("group", "general")
        if group not in settings:
            settings[group] = []
        settings[group].append(setting)

    return render_template("admin/settings/index.html", settings=settings)


@app.route("/admin/settings/update", methods=["POST"])
@login_required
def admin_settings_update():
    if not current_user.is_admin:
        abort(403)

    data = request.form.to_dict()

    for key, value in data.items():
        if key.startswith("setting_"):
            parts = key.split("_", 3)
            if len(parts) >= 3:
                setting_id = parts[1]
                language = parts[2]

                if language == "vi":
                    db.settings.update_one(
                        {"_id": ObjectId(setting_id)},
                        {"$set": {"value_vi": value, "updated_at": datetime.utcnow()}},
                    )
                elif language == "ja":
                    db.settings.update_one(
                        {"_id": ObjectId(setting_id)},
                        {"$set": {"value_ja": value, "updated_at": datetime.utcnow()}},
                    )

    flash("Cài đặt đã được cập nhật thành công", "success")
    return redirect(url_for("admin_settings"))


# Setup MongoDB and Initialize Data
# We're using existing app.py and models.py instead of implementing MongoDB
# because we already have a functioning PostgreSQL database
# and MongoDB isn't available

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
