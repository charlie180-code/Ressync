from flask import jsonify, render_template, request
from flask_login import login_required
from datetime import datetime
from ..models.general.marketingcampaign import MarketingCampaign
from ..models.general.company import Company
from .. import db
from . import advertise
from flask_babel import gettext as _


@advertise.route("/ads/<int:company_id>", methods=['POST', 'GET'])
@login_required
def ads(company_id):
    company = Company.query.get_or_404(company_id)
    if request.method == "POST":
        title = request.form.get("title")
        description = request.form.get("description")
        objectives = request.form.get("objectives")
        start_from = request.form.get("start_from")
        end_at = request.form.get("end_at")
        min_budget = request.form.get("min_budget")
        max_budget = request.form.get("max_budget")
        start_from_dt = datetime.fromisoformat(start_from)
        end_at_dt = datetime.fromisoformat(end_at)

        new_ad = MarketingCampaign(
            title=title,
            description=description,
            objectives=objectives,
            start_from=start_from_dt,
            end_at=end_at_dt,
            min_budget=min_budget,
            max_budget=max_budget,
            company_id=company.id
        )

        db.session.add(new_ad)
        db.session.commit()

        return jsonify(
            {
                'success' : True, 
                'title' : _('Campagne ajoutée'), 
                'message' :  _('Votre nouvelle campagne a été ajoutée, vous pouvez maintenant tirer le meilleur de votre audience'),
                'confirmButtonText' : _('OK')
            }
        ), 200

    ads = MarketingCampaign.query.all()
    return render_template("dashboard/@support_team/ads.html", ads=ads, company=company)


@advertise.route('/edit_ad/<int:ad_id>/<int:company_id>', methods=['POST'])
@login_required
def edit_ad(ad_id, company_id):
    ad = MarketingCampaign.query.get_or_404(ad_id)
    company = Company.query.get_or_404(company_id)
    data = request.json

    title = data.get('title')
    description = data.get('description')
    objectives = data.get('objectives')
    start_from = data.get('start_from')
    end_at = data.get('end_at')
    min_budget = data.get('min_budget')
    max_budget = data.get('max_budget')
    debt = data.get('debt')

    try:
        if not isinstance(start_from, str):
            start_from = str(start_from)
        if not isinstance(end_at, str):
            end_at = str(end_at)
            
        ad.title = title
        ad.description = description
        ad.objectives = objectives
        ad.start_from = datetime.fromisoformat(start_from)
        ad.end_at = datetime.fromisoformat(end_at)
        ad.min_budget = float(min_budget)
        ad.max_budget = float(max_budget)
        ad.debt = float(debt)
        ad.company_id = company.id

        db.session.commit()
        return jsonify(
            {
                'title': _('Campagne mise à jour!'),
                'success': True, 
                'message': _('Votre campagne a été bien mise à jour'),
                'confirmButtonText': _('OK')
            }
        ), 200
    except Exception as e:
        db.session.rollback()
        return jsonify(
            {
                'title': _('Erreur'),
                'success': False, 
                'message': str(e),
                'confirmButtonText' : _('OK')
            }
        ), 500
    

@advertise.route('/ads/delete_ad/<int:ad_id>/<int:company_id>', methods=['DELETE'])
@login_required
def delete_ad(ad_id, company_id):
    ad = MarketingCampaign.query.get_or_404(ad_id)
    company = Company.query.get_or_404(company_id)
    try:
        db.session.delete(ad)
        db.session.commit()
        return jsonify(
            {
                'success': True, 
                'message': _('Campagne supprimée')
            }
        ), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500