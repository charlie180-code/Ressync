from flask import render_template, request
from ..models.general.company import Company
from . import blog

@blog.route("/create_article/<int:company_id>")
def create_article(company_id):
    if request.method == 'POST':
        company = Company.query.get_or_404(company_id)
        