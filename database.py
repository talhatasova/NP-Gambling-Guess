from sqlalchemy import (
    create_engine, Column, Integer, String, ForeignKey,
    Table, Double, DateTime, Boolean, func, UniqueConstraint
)
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
import random
from datetime import datetime, timedelta
from exceptions import NoGamblerFoundException, CooldownException, DuplicateGuessException

Base = declarative_base()

class Gambler(Base):
    __tablename__ = 'gamblers'
    
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    correct = Column(Integer, default=0)
    wrong = Column(Integer, default=0)
    can_guess = Column(DateTime, nullable=False)
    
    # Relationship to guesses
    guesses = relationship("Guess", back_populates="gambler")
    
    def __repr__(self):
        return f"Name={self.name}, ID={self.id}"

class Round(Base):
    __tablename__ = 'rounds'

    id = Column(Integer, primary_key=True, autoincrement=True)
    isActive = Column(Boolean, nullable=False, default=True)
    number = Column(Integer, nullable=False)
    winner_id = Column(Integer, ForeignKey('gamblers.id'), nullable=True, default=None)
    start_time = Column(DateTime, nullable=True, default=func.now())
    end_time = Column(DateTime, nullable=True, default=None)
    
    # Relationship to guesses and gambler
    guesses = relationship("Guess", back_populates="round")
    winner = relationship("Gambler", back_populates="won_rounds")
    
    # Unique constraint on round number
    __table_args__ = (UniqueConstraint('number', name='uq_round_number'),)
    
    def __repr__(self):
        return f"<Round(number={self.number}, winner_id={self.winner_id})>"

class Guess(Base):
    __tablename__ = 'guesses'

    id = Column(Integer, primary_key=True)
    value = Column(Integer, nullable=False)
    isCorrect = Column(Boolean, nullable=False)
    timestamp = Column(DateTime, nullable=False, default=func.now())
    
    # Relationships to gambler and round
    gambler_id = Column(Integer, ForeignKey('gamblers.id'), nullable=False)
    round_id = Column(Integer, ForeignKey('rounds.id'), nullable=False)
    gambler = relationship("Gambler", back_populates="guesses")
    round = relationship("Round", back_populates="guesses")
    
    def __repr__(self):
        return f"<Guess(value={self.value}, isCorrect={self.isCorrect}, timestamp={self.timestamp})>"

# Add back_populates for related fields in Gambler
Gambler.won_rounds = relationship("Round", back_populates="winner")

engine = create_engine("sqlite:///game_database.db")  # Use SQLite for simplicity
Base.metadata.create_all(engine)

# Session
Session = sessionmaker(bind=engine)
session = Session()

# Helper Functions
def get_now() -> datetime:
    return datetime.now().replace(microsecond=0)

def add_gambler(gambler_id: int, name: str) -> Gambler:
    new_gambler = Gambler(
        id=gambler_id,
        name=name,
        can_guess=datetime.now()
    )
    session.add(new_gambler)
    session.commit()
    return new_gambler

def get_gambler(gambler_id: int) -> Gambler:
    return session.query(Gambler).filter(Gambler.id == gambler_id).first()

def get_current_round() -> Round:
    return session.query(Round).filter(Round.isActive == True).first()  # noqa: E712

def is_guess_correct(guess: int, current_round: Round) -> bool:
    return guess == current_round.number if current_round else False

def new_round():  
    # Create and add the new round
    new_round = Round(number=random.randint(1, 10000))
    session.add(new_round)
    session.commit()

def get_current_guess_num() -> int:
    current_round:Round = get_current_round()
    return session.query(Guess).filter(Guess.round_id == current_round.id).count()

def get_guesses() -> list[Guess]:
    current_round:Round = get_current_round()
    return session.query(Guess).filter(Guess.round_id == current_round.id).all()

def get_guess_by_value(value:int) -> Guess:
    current_round:Round = get_current_round()
    return session.query(Guess).filter(Guess.round_id == current_round.id).filter(Guess.value==value).first()

def make_guess(guess: int, gambler_id: int) -> bool:
    gambler = get_gambler(gambler_id)
    current_round = get_current_round()

    if not gambler:
        raise NoGamblerFoundException("You are not registered yet.")
    if not current_round:
        raise ValueError("No active round.")
    if gambler.can_guess > get_now():
        remaining_time:timedelta = gambler.can_guess - get_now()
        raise CooldownException(f"You cannot make a new guess for **{remaining_time.seconds}** seconds.")

    all_guess_so_far = [guess.value for guess in get_guesses()]
    if guess in all_guess_so_far:
        old_guess:Guess = get_guess_by_value(guess)
        old_guess_made_by:Gambler = get_gambler(old_guess.gambler_id)
        raise DuplicateGuessException(f"**{guess}** has already been made by **{old_guess_made_by.name}**. Pick another number.")

    # Determine if the guess is correct
    correct = is_guess_correct(guess, current_round)

    # Update guess record
    new_guess = Guess(
        value=guess,
        isCorrect=correct,
        gambler=gambler,
        round=current_round
    )
    session.add(new_guess)

    # Update gambler's statistics
    if correct:
        gambler.correct += 1
        current_round.isActive = False  # End the round if the guess is correct
        current_round.winner = gambler
        current_round.end_time = func.now()
        session.commit()  # Commit changes before starting a new round
        new_round()  # Start a new round
    else:
        gambler.wrong += 1

    gambler.can_guess = get_now() + timedelta(seconds=10)
    session.commit()
    return correct
