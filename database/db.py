from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from . import models


class Database:
    def __init__(self, db_url):
        engine = create_engine(db_url)
        models.Base.metadata.create_all(bind=engine)
        self.maker = sessionmaker(bind=engine)

    def _get_or_create(self, session, model, u_field, u_value, **data):
        db_data = session.query(model).filter(u_field == data[u_value]).first()
        if not db_data:
            db_data = model(**data)
        return db_data

    def create_post(self, data):
        session = self.maker()
        author = self._get_or_create(
            session, models.Author, models.Author.url, "url", **data["author"],
        )

        post = self._get_or_create(
            session, models.Post, models.Post.url, "url", **data["post_data"], author=author
        )
        post.tags.extend(
            map(
                lambda tag_data: self._get_or_create(
                    session, models.Tag, models.Tag.url, "url", **tag_data
                ),
                data["tags"],
            )
        )
        session.add(post)
        try:
            session.commit()
        except Exception as exc:
            print(exc)
            session.rollback()
        finally:
            session.close()

    def _get_or_create_comments(self, session, data: list):
        result = []
        for comment in data:
            comment_author = self._get_or_create(
                session,
                models.Author,
                models.Author.url,
                comment["comment"]["user"]["url"],
                name=comment["comment"]["user"]["full_name"],
                url=comment["comment"]["user"]["url"],
            )
            db_comment = self._get_or_create(
                session,
                models.Comment,
                models.Comment.id,
                comment["comment"]["id"],
                **comment["comment"],
                author=comment_author,
            )

            result.append(db_comment)
            result.extend(self._get_or_create_comments(session, comment["comment"]["children"]))

        return result
