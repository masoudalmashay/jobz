from app.extensions import db
from app.models.category import Category
from app.models.city import City

from app.models.package import Package

from run import app


# from app.models.package import Package
# from app.models.order import Order
# from app.models.job import Job


def city_seeder(cities):

    for city in cities:
        new_city = City(name=city)
        db.session.add(new_city)
    db.session.commit()

def category_seeder(categories):

    for category in categories:
        new_category = Category(name=category)
        db.session.add(new_category)
    db.session.commit()


cities = [
    "طرابلس", "بنغازي", "مصراتة", "الزاوية", "سبها", "سرت", "طبرق", "درنة", 
    "زليتن", "الخمس", "غريان", "البيضاء", "أجدابيا", "ترهونة", "يفرن", "نالوت", 
    "بني وليد", "مزدة", "زوارة", "المرج", "الواحات", "الكفرة", "غات", "أوباري", 
    "مرزق", "ودان", "هون", "سوكنة", "رأس لانوف", "البريقة", "تاورغاء", "مسلاتة", 
    "قصر الأخيار", "تاجوراء", "جنزور", "الماية", "الزنتان", "الرجبان", "الشويرف", 
    "براك الشاطئ", "تمسة", "أبو قرين", "الهيشة", "القريات", "الشاطئ", "غدامس", "زلة", 
    "العجيلات", "صرمان", "الجميل", "رقدالين", "زلطن", "أم الأرانب", "توكرة", "القيقب", 
    "السرير", "سلوق", "قمينس", "الأبرق", "التميمي", "الجغبوب", "المخيلي", "مسة", 
    "مرتوبة", "سوسة", "عين مارة", "البياضة", "الفائدية", "الأبيار", "المقرون", 
    "الزويتينة", "جالو", "أوجلة"
]

categories = [
    "تكنولوجيا المعلومات",
    "التسويق والإعلان",
    "المحاسبة والمالية",
    "الهندسة",
    "التصميم والإبداع",
    "المبيعات",
    "خدمة العملاء",
    "الطب والرعاية الصحية",
    "التعليم والتدريب",
    "الإدارة والسكرتارية",
    "الترجمة واللغات",
    "الصناعة والحرف",
    "اللوجستيات والنقل",
    "القانون والاستشارات",
    "الزراعة والثروة الحيوانية",
    "الضيافة والسياحة",
    "البحث والتطوير",
    "الكتابة والتحرير",
    "الإعلام والإنتاج",
    "العقارات والبناء",
    "العمل الحر (فريلانس)",
    "الأمن والحماية",
    "الخدمات الاجتماعية والإنسانية",
    "وظائف أخرى"
]



def package_seeder():
    packages = [
        {
            "name": "حزمة إعلان واحدة",
            "post_count": 1,
            "price": 30.0,
            "duration_days": 30
        },
        {
            "name": "حزمة 3 إعلانات",
            "post_count": 3,
            "price": 60.0,
            "duration_days": 30
        }
    ]

    for package in packages:
        new_package = Package(
            name=package['name'],
            post_count=package['post_count'],
            price=package['price'],
            duration_days=package['duration_days']
        )
        db.session.add(new_package)
    db.session.commit()


with app.app_context():
    package_seeder()

# def package_seeder(packages):

#     for package in packages:
#         new_package = Package(name=package['name'], post_count=package['post_count'], price=package['price'], duration_days=package['duration_days'])
#         db.session.add(new_package)
#     db.session.commit()

