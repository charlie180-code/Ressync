from ... import db

class Article(db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key=True)
    article_img_url = db.Column(db.String)
    title = db.Column(db.String(128), nullable=False)
    content = db.Column(db.Text, nullable=False)
    likes = db.Column(db.Integer, default=0)
    
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    author = db.relationship('User', backref='posts')

    def __init__(self, article_img_url, title, content, likes, company_id, user_id):
        self.article_img_url = article_img_url
        self.title = title
        self.content = content
        self.likes = likes
        self.company_id = company_id
        self.user_id = user_id

