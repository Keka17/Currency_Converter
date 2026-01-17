from app.models.models import User


def add_users(db):
    users = [
        User(
            username="Darth Vader",
            hashed_password="$2b$12$i02J5Fa/Cfnu.Dw.VNFMRu0FZqChAFfkHlQUK.4JUtKGbPiqUMLYS",
            is_admin=False,
        ),
        User(
            username="Aragorn II",
            hashed_password="$2b$12$9PYxbs1o61b7g8arw.EICe4EXi30iTcC1boZ1IWYd51g.F.mBek/u",
            is_admin=True,
        ),
        User(
            username="Hermione G.",
            hashed_password="$2b$12$mh5vjfbDrBhvjVHuTnc98uacN0LQhDtJ71UB29LMkM6bnIjKrn97y",  # Str0ngP@ssword
            is_admin=False,
        ),
    ]
    db.add_all(users)
    db.flush()
