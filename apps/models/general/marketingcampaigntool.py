from ... import db
class MarketingCampaignTool(db.Model):
    __tablename__ = 'marketing_campaign_tools'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    description = db.Column(db.Text)
    cost = db.Column(db.Float)

marketing_campaign_tool_association = db.Table('marketing_campaign_tool_association', db.Model.metadata,
    db.Column('marketing_campaign_id', db.Integer, db.ForeignKey('marketing_campaigns.id')),
    db.Column('marketing_campaign_tool_id', db.Integer, db.ForeignKey('marketing_campaign_tools.id'))
)

