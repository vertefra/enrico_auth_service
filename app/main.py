from fastapi import Depends, FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from httpx import AsyncClient
from models import User
from database import SessionLocal, engine
from sqlalchemy.orm import Session
from models import User
import models
import uvicorn


models.Base.metadata.create_all(bind=engine)

app = FastAPI(debug=True)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

carol_bus = "http://127.0.0.1:3005"


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# event listener from bus =====================================


@app.post('/events')
async def event_listener(event: dict):
    print("Carol dispatched a new event: ", event)
    # test end

    return ({'status': 'event received'})

# ==============================================================


@app.post('/signup/')
async def signup(data: dict, db: Session = Depends(get_db)):
    username = data['username']
    sid = data['sid']

    try:
        new_user = User()
        new_user.username = username
        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        try:
            async with AsyncClient() as client:
                res = await client.post(f"{carol_bus}/events",
                                        json={"type": "userSignUp", "payload": {'username': username, 'sid': sid}})
            print(res)
        except Exception as err:
            print(err)

        return ({'signup': True, 'user': {'username': username, 'sid': sid}})

    except Exception as err:
        print("ERROR ", err)
        db.rollback()
        return HTTPException(status_code=500, detail=err)


@app.post('/join')
async def join(data: dict, session: Session = Depends(get_db)):
    print("joining --> ", data)
    username = data['username']
    sid = data['sid']

    try:
        login_user = session.query(User).filter_by(
            username=username).one_or_none()
    except Exception as err:
        print(err)

    print(f"{login_user} is joining")

    if(login_user):
        try:
            async with AsyncClient() as client:
                res = await client.post(f"{carol_bus}/events",
                                        json={"type": "userJoin", "payload": {'username': username, 'sid': sid}})
            print("response: ", res)
        except Exception as err:
            print('err', err)

        return ({"joined": True, "username": login_user.username, 'sid': sid})
    else:
        return HTTPException(status_code=500, detail="login failed")


if __name__ == "__main__":
    print("running?")
    uvicorn.run(app, host="127.0.0.1", port=3003)
