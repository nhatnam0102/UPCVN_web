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
)
from flask_login import (
    LoginManager,
    current_user,
    login_user,
    logout_user,
    login_required,
)
from werkzeug.utils import secure_filename
from datetime import datetime
from pymongo import MongoClient
from bson.objectid import ObjectId
import json
from werkzeug.routing import BaseConverter
import base64


# Custom URL converter for ObjectId
class ObjectIdConverter(BaseConverter):
    def to_python(self, value):
        return ObjectId(value)

    def to_url(self, value):
        return str(value)


# Setup MongoDB connection
mongo_client = MongoClient(os.environ.get("MONGODB_URI", "mongodb://localhost:27017"))
db = mongo_client.get_database(os.environ.get("MONGODB_DB_NAME", "upcvn"))

# App setup
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "your-secret-key")
app.config["UPLOAD_FOLDER"] = "static/images/uploads"
app.config["ALLOWED_EXTENSIONS"] = {"png", "jpg", "jpeg", "gif"}

# Register the custom converter
app.url_map.converters["ObjectId"] = ObjectIdConverter

# Initialize extensions
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"
login_manager.login_message = "Vui lòng đăng nhập để truy cập trang này."

# Import models and setup
with app.app_context():
    from models import db_setup

    User, Product, CaseStudy, News, Contact, Setting, Partner = db_setup(db)

    # Create default company settings if they don't exist
    if db.settings.count_documents({"group": "company"}) == 0:
        # Default company settings
        default_settings = [
            {
                "key": "company_title",
                "value_vi": "Về chúng tôi",
                "value_ja": "私たちについて",
                "group": "company",
            },
            {
                "key": "company_description",
                "value_vi": "アルティメイトプロジェクト株式会社 là công ty chuyên cung cấp các giải pháp công nghệ tiên tiến, với cam kết mang đến dịch vụ tốt nhất cho khách hàng.",
                "value_ja": "アルティメイトプロジェクト株式会社は、お客様にご満足いただける最高のサービスをご提供することをお約束した先進的なテクノロジーソリューションを提供する会社です。",
                "group": "company",
            },
            {
                "key": "company_vision",
                "value_vi": "Tầm nhìn của chúng tôi là trở thành đối tác tin cậy, cung cấp những giải pháp hiệu quả, đơn giản và dễ sử dụng, giúp khách hàng tối ưu hóa hoạt động kinh doanh.",
                "value_ja": "私たちのビジョンは、信頼できるパートナーとなり、効果的でシンプル、使いやすいソリューションを提供し、お客様のビジネス運営を最適化することです。",
                "group": "company",
            },
            {
                "key": "company_history",
                "value_vi": "Thành lập từ năm 2010, chúng tôi đã không ngừng phát triển và hoàn thiện các sản phẩm, dịch vụ, mang lại giá trị thực cho nhiều doanh nghiệp trong nhiều lĩnh vực khác nhau.",
                "value_ja": "2010年の設立以来、私たちは製品やサービスを絶えず開発・改善し、様々な分野の多くの企業に実質的な価値をもたらしてきました。",
                "group": "company",
            },
            {
                "key": "company_address",
                "value_vi": "Địa chỉ: Tokyo, Nhật Bản",
                "value_ja": "住所：東京、日本",
                "group": "company",
            },
            {
                "key": "company_phone",
                "value_vi": "Điện thoại: +81-XX-XXXX-XXXX",
                "value_ja": "電話：+81-XX-XXXX-XXXX",
                "group": "company",
            },
            {
                "key": "company_email",
                "value_vi": "Email: info@u-mate.co.jp",
                "value_ja": "メール：info@u-mate.co.jp",
                "group": "company",
            },
        ]

        db.settings.insert_many(default_settings)


def encode_image_to_base64(filepath):
    """Helper function to encode an image file to Base64."""
    with open(filepath, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


def insert_default_data():
    # Insert default products
    if db.products.count_documents({}) == 0:
        default_products = [
            {
                "title_vi": "BT Cloud",
                "title_ja": "BTクラウド",
                "description_vi": "Giải pháp quản lý doanh nghiệp toàn diện trên nền tảng điện toán đám mây.",
                "description_ja": "クラウドベースの包括的なビジネス管理ソリューション。",
                "image": encode_image_to_base64("static/images/products/bt_cloud.jpg"),
                "order": 1,
            },
            {
                "title_vi": "Giải pháp AI",
                "title_ja": "AIソリューション",
                "description_vi": "Ứng dụng trí tuệ nhân tạo vào quy trình sản xuất và kiểm soát chất lượng.",
                "description_ja": "製造工程と品質管理への人工知能の応用。",
                "image": encode_image_to_base64("static/images/products/ai.jpg"),
                "order": 2,
            },
            # ... Add more products as needed ...
        ]
        db.products.insert_many(default_products)

    # Insert default case studies
    if db.case_studies.count_documents({}) == 0:
        default_case_studies = [
            {
                "title_vi": "Tích hợp Kintone",
                "title_ja": "kintone統合",
                "description_vi": "Tích hợp nền tảng kintone với các hệ thống nội bộ của doanh nghiệp.",
                "description_ja": "kintoneプラットフォームと企業の内部システムの統合。",
                "category_vi": "Tích hợp",
                "category_ja": "統合",
                "image": encode_image_to_base64(
                    "static/images/case_studies/case_kintone.jpg"
                ),
                "order": 1,
            },
            {
                "title_vi": "Kiểm tra AI",
                "title_ja": "AI検査",
                "description_vi": "Hệ thống kiểm tra chất lượng tự động sử dụng trí tuệ nhân tạo.",
                "description_ja": "人工知能を使用した自動品質検査システム。",
                "category_vi": "Công nghệ AI",
                "category_ja": "AI技術",
                "image": encode_image_to_base64(
                    "static/images/case_studies/case_ai_inspection.jpg"
                ),
                "order": 2,
            },
            # ... Add more case studies as needed ...
        ]
        db.case_studies.insert_many(default_case_studies)

    # Insert default news
    if db.news.count_documents({}) == 0:
        default_news = [
            {
                "title_vi": "Khai trương văn phòng mới",
                "title_ja": "新オフィスオープン",
                "description_vi": "U-Mate khai trương văn phòng mới tại Hà Nội, mở rộng hoạt động kinh doanh.",
                "description_ja": "U-Mateがハノイに新オフィスをオープンし、事業を拡大。",
                "content_vi": "Chi tiết về khai trương văn phòng mới của U-Mate tại Hà Nội.",
                "content_ja": "ハノイにおけるU-Mateの新オフィスオープンについての詳細。",
                "date": datetime.strptime("2025-01-15", "%Y-%m-%d"),
            },
            {
                "title_vi": "Hợp tác với Microsoft",
                "title_ja": "マイクロソフトとの提携",
                "description_vi": "U-Mate trở thành đối tác chính thức của Microsoft tại Việt Nam.",
                "description_ja": "U-Mateがベトナムにおけるマイクロソフトの正式パートナーに。",
                "content_vi": "Chi tiết về hợp tác với Microsoft của U-Mate.",
                "content_ja": "U-Mateとマイクロソフトとのパートナーシップについての詳細。",
                "date": datetime.strptime("2025-02-20", "%Y-%m-%d"),
            },
            # ... Add more news as needed ...
        ]
        db.news.insert_many(default_news)

    # Insert default partners
    if db.partners.count_documents({}) == 0:
        default_partners = [
            {
                "name_vi": "Đối tác A",
                "name_ja": "パートナーA",
                "website": "https://partner-a.com",
                "image": encode_image_to_base64("static/images/partners/partner_a.png"),
                "order": 1,
            },
            {
                "name_vi": "Đối tác B",
                "name_ja": "パートナーB",
                "website": "https://partner-b.com",
                "image": encode_image_to_base64("static/images/partners/partner_b.png"),
                "order": 2,
            },
            # ... Add more partners as needed ...
        ]
        db.partners.insert_many(default_partners)


# Call the function during application initialization
with app.app_context():
    insert_default_data()


# Login manager user loader
@login_manager.user_loader
def load_user(user_id):
    user_data = db.users.find_one({"_id": ObjectId(user_id)})
    return User(user_data) if user_data else None


# Language and translation setup
@app.before_request
def before_request():
    g.language = request.cookies.get("language", "vi")

    if g.language == "vi":
        from translations.vi import translations
    else:
        from translations.ja import translations

    g.translations = translations

    # Fetch company settings and make them globally available
    company_settings = {}
    settings = db.settings.find({"group": "company"})
    for setting in settings:
        value = (
            setting.get("value_vi") if g.language == "vi" else setting.get("value_ja")
        )
        company_settings[setting["key"]] = value or ""
    g.company_settings = company_settings


@app.route("/change-language/<language>")
def change_language(language):
    # Only allow valid languages
    if language not in ["vi", "ja"]:
        language = "vi"

    # Get the referring page or default to home
    referrer = request.referrer or url_for("index")
    response = redirect(referrer)

    # Set the language cookie
    response.set_cookie("language", language, max_age=60 * 60 * 24 * 30)  # 30 days

    return response


# Helper functions
def allowed_file(filename):
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in app.config["ALLOWED_EXTENSIONS"]
    )


def save_uploaded_file(file):
    if file and allowed_file(file.filename):
        # Read the file content and encode it as Base64
        file_content = file.read()
        encoded_image = base64.b64encode(file_content).decode("utf-8")
        return encoded_image
    return None


# Public routes
@app.route("/")
def index():
    # Fetch data from MongoDB
    products = list(db.products.find().sort("order", 1))
    case_studies = list(db.case_studies.find().sort("order", 1))
    news_items = list(db.news.find().sort("date", -1).limit(3))
    partners = list(db.partners.find().sort("order", 1))  # Fetch partners data

    # Fetch company settings
    company_settings = {}
    settings = db.settings.find({"group": "company"})
    for setting in settings:
        value = (
            setting.get("value_vi") if g.language == "vi" else setting.get("value_ja")
        )
        company_settings[setting["key"]] = value or ""

    for product in products:
        if "image" in product:
            product["image"] = f"data:image/png;base64,{product['image']}"

    for partner in partners:
        if "image" in partner:
            partner["image"] = f"data:image/png;base64,{partner['image']}"

    return render_template(
        "index.html",
        products=products,
        case_studies=case_studies,
        news_items=news_items,
        partners=partners,  # Pass partners data to the template
        company_settings=company_settings,
    )


@app.route("/product/<string:id>")
def product_detail(id):
    product = db.products.find_one({"_id": ObjectId(id)})
    if not product:
        abort(404)
    return render_template("product_detail.html", product=product)


@app.route("/case-study/<string:id>")
def case_study_detail(id):
    case_study = db.case_studies.find_one({"_id": ObjectId(id)})
    if not case_study:
        abort(404)
    return render_template("case_study_detail.html", case_study=case_study)


@app.route("/contact", methods=["GET", "POST"])
def contact():
    # Fetch company settings for footer
    company_settings = {}
    settings = db.settings.find({"group": "company"})
    for setting in settings:
        value = (
            setting.get("value_vi") if g.language == "vi" else setting.get("value_ja")
        )
        company_settings[setting["key"]] = value or ""

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
            return render_template(
                "contact_success.html", company_settings=company_settings
            )
        else:
            flash("Vui lòng điền đầy đủ thông tin bắt buộc.", "danger")

    return render_template("contact.html", company_settings=company_settings)


# Admin authentication routes
@app.route("/admin/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("admin_dashboard"))

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        user_data = db.users.find_one({"username": username})

        if user_data:
            user = User(user_data)  # Wrap the dictionary in the User class
            if user.check_password(password):
                login_user(user)
                next_page = request.args.get("next")
                return redirect(next_page or url_for("admin_dashboard"))

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
    partners_count = db.partners.count_documents({})

    return render_template(
        "admin/dashboard.html",
        products_count=products_count,
        case_studies_count=case_studies_count,
        news_count=news_count,
        contacts_count=contacts_count,
        unread_contacts=unread_contacts,
        partners_count=partners_count,
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
        order = request.form.get("order", 0)

        # Handle image upload
        image = request.files.get("image")
        image_base64 = save_uploaded_file(image)

        if title_vi and title_ja and description_vi and description_ja and image_base64:
            new_product = {
                "title_vi": title_vi,
                "title_ja": title_ja,
                "description_vi": description_vi,
                "description_ja": description_ja,
                "image": image_base64,
                "order": order,
            }
            db.products.insert_one(new_product)
            flash("Sản phẩm đã được tạo thành công", "success")
            return redirect(url_for("admin_products"))
        else:
            flash("Vui lòng điền đầy đủ thông tin bắt buộc", "danger")

    return render_template("admin/products/create.html")


@app.route("/admin/products/edit/<string:id>", methods=["GET", "POST"])
@login_required
def admin_products_edit(id):
    if not current_user.is_admin:
        abort(403)

    product = db.products.find_one({"_id": ObjectId(id)})

    if not product:
        abort(404)  # Return 404 if the product is not found

    if request.method == "POST":
        update_data = {
            "title_vi": request.form.get("title_vi"),
            "title_ja": request.form.get("title_ja"),
            "description_vi": request.form.get("description_vi"),
            "description_ja": request.form.get("description_ja"),
            "order": request.form.get("order", 0),
        }

        # Handle image upload if new image is provided
        image = request.files.get("image")
        if image and image.filename:
            image_base64 = save_uploaded_file(image)
            if image_base64:
                update_data["image"] = image_base64

        db.products.update_one({"_id": ObjectId(id)}, {"$set": update_data})
        flash("Sản phẩm đã được cập nhật thành công", "success")
        return redirect(url_for("admin_products"))

    return render_template("admin/products/edit.html", product=product)


@app.route("/admin/products/delete/<string:id>", methods=["POST"])
@login_required
def admin_products_delete(id):
    if not current_user.is_admin:
        abort(403)

    db.products.delete_one({"_id": ObjectId(id)})
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
        order = request.form.get("order", 0)

        # Handle image upload
        image = request.files.get("image")
        image_base64 = save_uploaded_file(image)

        if (
            title_vi
            and title_ja
            and description_vi
            and description_ja
            and category_vi
            and category_ja
            and image_base64
        ):
            new_case_study = {
                "title_vi": title_vi,
                "title_ja": title_ja,
                "description_vi": description_vi,
                "description_ja": description_ja,
                "category_vi": category_vi,
                "category_ja": category_ja,
                "image": image_base64,
                "order": order,
            }
            db.case_studies.insert_one(new_case_study)
            flash("Dự án đã được tạo thành công", "success")
            return redirect(url_for("admin_case_studies"))
        else:
            flash("Vui lòng điền đầy đủ thông tin bắt buộc", "danger")

    return render_template("admin/case_studies/create.html")


@app.route("/admin/case-studies/edit/<string:id>", methods=["GET", "POST"])
@login_required
def admin_case_studies_edit(id):
    if not current_user.is_admin:
        abort(403)

    case_study = db.case_studies.find_one({"_id": ObjectId(id)})

    if not case_study:
        abort(404)  # Return 404 if the case study is not found

    if request.method == "POST":
        update_data = {
            "title_vi": request.form.get("title_vi"),
            "title_ja": request.form.get("title_ja"),
            "description_vi": request.form.get("description_vi"),
            "description_ja": request.form.get("description_ja"),
            "category_vi": request.form.get("category_vi"),
            "category_ja": request.form.get("category_ja"),
            "order": request.form.get("order", 0),
        }

        # Handle image upload if new image is provided
        image = request.files.get("image")
        if image and image.filename:
            image_base64 = save_uploaded_file(image)
            if image_base64:
                update_data["image"] = image_base64

        db.case_studies.update_one({"_id": ObjectId(id)}, {"$set": update_data})
        flash("Dự án đã được cập nhật thành công", "success")
        return redirect(url_for("admin_case_studies"))

    return render_template("admin/case_studies/edit.html", case_study=case_study)


@app.route("/admin/case-studies/delete/<string:id>", methods=["POST"])
@login_required
def admin_case_studies_delete(id):
    if not current_user.is_admin:
        abort(403)

    db.case_studies.delete_one({"_id": ObjectId(id)})
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
                date = datetime.strptime(
                    date_str, "%Y-%m-%d"
                )  # Convert to datetime.datetime
                new_news = {
                    "title_vi": title_vi,
                    "title_ja": title_ja,
                    "description_vi": description_vi,
                    "description_ja": description_ja,
                    "content_vi": content_vi,
                    "content_ja": content_ja,
                    "date": date,
                }
                db.news.insert_one(new_news)
                flash("Tin tức đã được tạo thành công", "success")
                return redirect(url_for("admin_news"))
            except ValueError:
                flash("Định dạng ngày không hợp lệ", "danger")
        else:
            flash("Vui lòng điền đầy đủ thông tin bắt buộc", "danger")

    return render_template("admin/news/create.html")


@app.route("/admin/news/edit/<string:id>", methods=["GET", "POST"])
@login_required
def admin_news_edit(id):
    if not current_user.is_admin:
        abort(403)

    news = db.news.find_one({"_id": ObjectId(id)})

    if request.method == "POST":
        update_data = {
            "title_vi": request.form.get("title_vi"),
            "title_ja": request.form.get("title_ja"),
            "description_vi": request.form.get("description_vi"),
            "description_ja": request.form.get("description_ja"),
            "content_vi": request.form.get("content_vi"),
            "content_ja": request.form.get("content_ja"),
        }
        date_str = request.form.get("date")

        try:
            update_data["date"] = datetime.strptime(
                date_str, "%Y-%m-%d"
            )  # Convert to datetime.datetime
            db.news.update_one({"_id": ObjectId(id)}, {"$set": update_data})
            flash("Tin tức đã được cập nhật thành công", "success")
            return redirect(url_for("admin_news"))
        except ValueError:
            flash("Định dạng ngày không hợp lệ", "danger")

    return render_template("admin/news/edit.html", news=news)


@app.route("/admin/news/delete/<string:id>", methods=["POST"])
@login_required
def admin_news_delete(id):
    if not current_user.is_admin:
        abort(403)

    db.news.delete_one({"_id": ObjectId(id)})
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


@app.route("/admin/contacts/view/<string:id>")
@login_required
def admin_contacts_view(id):
    if not current_user.is_admin:
        abort(403)

    contact = db.contacts.find_one({"_id": ObjectId(id)})

    # Mark as read if it wasn't already
    if not contact.get("is_read"):
        db.contacts.update_one({"_id": ObjectId(id)}, {"$set": {"is_read": True}})

    # Define nl2br function to convert newlines to <br> tags
    def nl2br(value):
        return value.replace("\n", "<br>")

    # Add the filter to Jinja environment
    app.jinja_env.filters["nl2br"] = nl2br

    return render_template("admin/contacts/view.html", contact=contact)


@app.route("/admin/contacts/delete/<string:id>", methods=["POST"])
@login_required
def admin_contacts_delete(id):
    if not current_user.is_admin:
        abort(403)

    db.contacts.delete_one({"_id": ObjectId(id)})
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
        if setting["group"] not in settings:
            settings[setting["group"]] = []
        settings[setting["group"]].append(setting)

    return render_template("admin/settings/index.html", settings=settings)


@app.route("/admin/settings/update", methods=["POST"])
@login_required
def admin_settings_update():
    if not current_user.is_admin:
        abort(403)

    data = request.form.to_dict()

    for key, value in data.items():
        if key.startswith("setting_"):
            parts = key.split("_")
            if len(parts) >= 4:
                setting_id = parts[1]
                language = parts[2]
                setting = db.settings.find_one({"_id": ObjectId(setting_id)})

                if setting:
                    if language == "vi":
                        db.settings.update_one(
                            {"_id": ObjectId(setting_id)}, {"$set": {"value_vi": value}}
                        )
                    elif language == "ja":
                        db.settings.update_one(
                            {"_id": ObjectId(setting_id)}, {"$set": {"value_ja": value}}
                        )

    flash("Cài đặt đã được cập nhật thành công", "success")
    return redirect(url_for("admin_settings"))


# Partner admin routes
@app.route("/admin/partners")
@login_required
def admin_partners():
    if not current_user.is_admin:
        abort(403)

    partners = list(db.partners.find().sort("order", 1))
    return render_template("admin/partners/index.html", partners=partners)


@app.route("/admin/partners/create", methods=["GET", "POST"])
@login_required
def admin_partners_create():
    if not current_user.is_admin:
        abort(403)

    if request.method == "POST":
        name_vi = request.form.get("name_vi")
        name_ja = request.form.get("name_ja")
        website = request.form.get("website")
        order = request.form.get("order", 0)

        # Handle image upload
        image = request.files.get("image")
        image_base64 = save_uploaded_file(image)

        if name_vi and name_ja and image_base64:
            new_partner = {
                "name_vi": name_vi,
                "name_ja": name_ja,
                "website": website,
                "image": image_base64,
                "order": order,
            }
            db.partners.insert_one(new_partner)
            flash("Đối tác đã được tạo thành công", "success")
            return redirect(url_for("admin_partners"))
        else:
            flash("Vui lòng điền đầy đủ thông tin bắt buộc", "danger")

    return render_template("admin/partners/create.html")


@app.route("/admin/partners/edit/<string:id>", methods=["GET", "POST"])
@login_required
def admin_partners_edit(id):
    if not current_user.is_admin:
        abort(403)

    partner = db.partners.find_one({"_id": ObjectId(id)})

    if request.method == "POST":
        update_data = {
            "name_vi": request.form.get("name_vi"),
            "name_ja": request.form.get("name_ja"),
            "website": request.form.get("website"),
            "order": request.form.get("order", 0),
        }

        # Handle image upload if new image is provided
        image = request.files.get("image")
        if image and image.filename:
            image_base64 = save_uploaded_file(image)
            if image_base64:
                update_data["image"] = image_base64

        db.partners.update_one({"_id": ObjectId(id)}, {"$set": update_data})
        flash("Đối tác đã được cập nhật thành công", "success")
        return redirect(url_for("admin_partners"))

    return render_template("admin/partners/edit.html", partner=partner)


@app.route("/admin/partners/delete/<string:id>", methods=["POST"])
@login_required
def admin_partners_delete(id):
    if not current_user.is_admin:
        abort(403)

    db.partners.delete_one({"_id": ObjectId(id)})
    flash("Đối tác đã được xóa thành công", "success")
    return redirect(url_for("admin_partners"))


# API routes for admin
@app.route("/api/admin/setup", methods=["POST"])
def api_setup_admin():
    # Check if any admin exists
    if db.users.count_documents({"is_admin": True}) > 0:
        return jsonify({"error": "Admin already exists"}), 400

    data = request.get_json()

    if (
        not data
        or "username" not in data
        or "password" not in data
        or "email" not in data
    ):
        return jsonify({"error": "Missing required fields"}), 400

    username = data.get("username")
    password = data.get("password")
    email = data.get("email")

    admin = {
        "username": username,
        "email": email,
        "is_admin": True,
        "password_hash": User.generate_password_hash(password),
    }

    db.users.insert_one(admin)

    return jsonify({"success": "Admin user created successfully"}), 201


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
