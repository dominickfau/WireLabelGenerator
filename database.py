from __future__ import annotations
import datetime
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, relationship, validates
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey,
    Float,
    Boolean,
    UniqueConstraint,
    Index,
)

from utilities import User

DeclarativeBase = declarative_base()

backend_logger = logging.getLogger("backend")


def create_tables(engine):
    backend_logger.info("Creating tables...")
    DeclarativeBase.metadata.create_all(engine)


def drop_tables(engine):
    backend_logger.info("Dropping tables...")
    DeclarativeBase.metadata.drop_all(engine)


class Base(DeclarativeBase):
    __abstract__ = True

    id = Column(Integer, primary_key=True)
    date_created = Column(DateTime, default=datetime.datetime.now)
    date_modified = Column(DateTime, default=datetime.datetime.now)


class Wire(Base):
    """Represents a wire."""

    __tablename__ = "wire"
    __table_args__ = (
        UniqueConstraint("color", "gauge", "insulation_type", name="UC_wire"),
        Index("IDX_wire_color", "color"),
        Index("IDX_wire_gauge", "gauge"),
    )

    color = Column(String(100), nullable=False)
    gauge = Column(Integer, nullable=False)
    insulation_type = Column(String(10), nullable=False)
    number = Column(String(256))

    articles = relationship("Article", back_populates="wire")  # type: list[Article]

    @validates("color")
    def validate_color(self, key, value):
        value = value.upper()
        self.date_modified = datetime.datetime.now()
        return value

    @validates("gauge")
    def validate_gauge(self, key, value):
        self.date_modified = datetime.datetime.now()
        return value

    @validates("insulation_type")
    def validate_insulation_type(self, key, value):
        value = value.upper()
        self.date_modified = datetime.datetime.now()
        return value

    @validates("number")
    def validate_number(self, key, value):
        self.date_modified = datetime.datetime.now()
        return value

    @property
    def description(self):
        return f"{self.gauge}GA {self.color} {self.insulation_type}"

    def __repr__(self):
        return f"<Wire {self.description}>"

    @staticmethod
    def find_by_gauge_color_type(session, gauge, color, insulation_type):
        return (
            session.query(Wire)
            .filter(
                Wire.gauge == gauge,
                Wire.color == color,
                Wire.insulation_type == insulation_type,
            )
            .first()
        )


class Terminal(Base):
    """Represents a terminal."""

    __tablename__ = "terminal"
    __table_args__ = (Index("IDX_terminal_description", "description"),)

    description = Column(String(256), nullable=False, unique=True)
    number = Column(String(256))
    strip_length = Column(Float, nullable=False)
    strip_gap = Column(Float, nullable=False)

    # articles = relationship("Article", back_populates="terminal")  # type: list[Article]

    @validates("description")
    def validate_description(self, key, value):
        self.date_modified = datetime.datetime.now()
        return value

    @validates("number")
    def validate_number(self, key, value):
        self.date_modified = datetime.datetime.now()
        return value

    @validates("strip_length")
    def validate_strip_length(self, key, value):
        self.date_modified = datetime.datetime.now()
        return value

    @validates("strip_gap")
    def validate_strip_gap(self, key, value):
        self.date_modified = datetime.datetime.now()
        return value

    def __repr__(self):
        return f"<Terminal {self.description}>"

    @staticmethod
    def find_by_description(session, description):
        return session.query(Terminal).filter_by(description=description).first()


class Article(Base):
    """Represents a wire with a length and terminals on both ends."""

    __tablename__ = "article"
    __table_args__ = (
        UniqueConstraint(
            "wire_id",
            "left_terminal_id",
            "right_terminal_id",
            "length",
            "part_number",
            "quantity",
            name="UC_article",
        ),
        Index("IDX_article_wire_id", "wire_id"),
        Index("IDX_article_left_terminal_id", "left_terminal_id"),
        Index("IDX_article_right_terminal_id", "right_terminal_id"),
    )

    wire_id = Column(Integer, ForeignKey("wire.id"), nullable=False)
    left_terminal_id = Column(Integer, ForeignKey("terminal.id"), nullable=False)
    apply_left_terminal = Column(Boolean, nullable=False)
    right_terminal_id = Column(Integer, ForeignKey("terminal.id"), nullable=False)
    apply_right_terminal = Column(Boolean, nullable=False)
    length = Column(Float, nullable=False)
    part_number = Column(String(256))
    quantity = Column(Integer, nullable=False)

    wire = relationship("Wire", back_populates="articles")  # type: Wire
    left_terminal = relationship(
        "Terminal", foreign_keys=[left_terminal_id]
    )  # type: Terminal
    right_terminal = relationship(
        "Terminal", foreign_keys=[right_terminal_id]
    )  # type: Terminal

    @validates("wire_id")
    def validate_wire_id(self, key, value):
        self.date_modified = datetime.datetime.now()
        return value

    @validates("left_terminal_id")
    def validate_left_terminal_id(self, key, value):
        self.date_modified = datetime.datetime.now()
        return value

    @validates("apply_left_terminal")
    def validate_apply_left_terminal(self, key, value):
        self.date_modified = datetime.datetime.now()
        return value

    @validates("right_terminal_id")
    def validate_right_terminal_id(self, key, value):
        self.date_modified = datetime.datetime.now()
        return value

    @validates("apply_right_terminal")
    def validate_apply_right_terminal(self, key, value):
        self.date_modified = datetime.datetime.now()
        return value

    @validates("length")
    def validate_length(self, key, value):
        self.date_modified = datetime.datetime.now()
        return value

    @staticmethod
    def find_by_part_number(session, part_number: str) -> list[Article]:
        return session.query(Article).filter_by(part_number=part_number).first()


def create_test_data(session_maker):
    terminals = [
        Terminal(
            description="14/16 AMPHENOL SOCKET", strip_length=0.18, strip_gap=0.12
        ),
        Terminal(description="14/16 AMPHENOL PIN", strip_length=0.18, strip_gap=0.12),
        Terminal(
            description="10/12 AMPHENOL SOCKET", strip_length=0.24, strip_gap=0.16
        ),
        Terminal(description="10/12 AMPHENOL PIN", strip_length=0.24, strip_gap=0.16),
        Terminal(description="14/16 0.250 FM QD", strip_length=0.3, strip_gap=0.2),
        Terminal(description="14/16 0.250 M QD", strip_length=0.3, strip_gap=0.2),
        Terminal(description="14/16 0.188 FM QD", strip_length=0.3, strip_gap=0.2),
        Terminal(description="14/16 0.188 M QD", strip_length=0.3, strip_gap=0.2),
        Terminal(description="10/12 0.250 FM QD", strip_length=0.3, strip_gap=0.2),
        Terminal(description="10/12 0.250 M QD", strip_length=0.3, strip_gap=0.2),
        Terminal(description="10/12 0.188 FM QD", strip_length=0.3, strip_gap=0.2),
        Terminal(description="10/12 0.188 M QD", strip_length=0.3, strip_gap=0.2),
        Terminal(description="14/16 MNL1 SOCKET", strip_length=0.18, strip_gap=0.12),
        Terminal(description="14/16 MNL1 PIN", strip_length=0.18, strip_gap=0.12),
        Terminal(description="14/16 MNL2 SOCKET", strip_length=0.18, strip_gap=0.12),
        Terminal(description="14/16 MNL2 PIN", strip_length=0.18, strip_gap=0.12),
        Terminal(description="10/12 MNL1 SOCKET", strip_length=0.25, strip_gap=0.12),
        Terminal(description="10/12 MNL1 PIN", strip_length=0.25, strip_gap=0.12),
        Terminal(description="10/12 MNL2 SOCKET", strip_length=0.25, strip_gap=0.12),
        Terminal(description="10/12 MNL2 PIN", strip_length=0.25, strip_gap=0.12),
        Terminal(description="SPLICE", strip_length=0.5, strip_gap=0.3),
    ]

    wires = [
        Wire(color="GRAY/BLACK", gauge=16, insulation_type="GPT", number="BC-175941"),
        Wire(color="RED", gauge=14, insulation_type="GPT", number="BC-175944"),
        Wire(color="BLACK", gauge=6, insulation_type="GPT", number="BC-175946"),
        Wire(color="RED", gauge=6, insulation_type="GPT", number="BC-175947"),
        Wire(color="YELLOW", gauge=14, insulation_type="GPT", number="BC-175951"),
        Wire(color="BROWN", gauge=14, insulation_type="GPT", number="BC-175954"),
        Wire(color="GREEN", gauge=16, insulation_type="GPT", number="BC-175956"),
        Wire(color="BROWN/BLUE", gauge=14, insulation_type="GPT", number="BC-175958"),
        Wire(color="BROWN/ORANGE", gauge=14, insulation_type="GPT", number="BC-175959"),
        Wire(color="RED/PURPLE", gauge=14, insulation_type="GPT", number="BC-175961"),
        Wire(color="RED/YELLOW", gauge=14, insulation_type="GPT", number="BC-175963"),
        Wire(color="RED", gauge=8, insulation_type="GPT", number="BC-175964"),
        Wire(color="BLACK", gauge=8, insulation_type="GPT", number="BC-175965"),
        Wire(color="RED", gauge=10, insulation_type="GPT", number="BC-175966"),
        Wire(color="BLACK", gauge=10, insulation_type="GPT", number="BC-175967"),
        Wire(color="BLACK", gauge=12, insulation_type="GPT", number="BC-175969"),
        Wire(color="BLACK", gauge=16, insulation_type="GPT", number="BC-175970"),
        Wire(color="GRAY/GREEN", gauge=16, insulation_type="GPT", number="BC-175971"),
        Wire(color="TAN", gauge=16, insulation_type="GPT", number="BC-175973"),
        Wire(color="BROWN/ORANGE", gauge=16, insulation_type="GPT", number="BC-175974"),
        Wire(color="BROWN/WHITE", gauge=16, insulation_type="GPT", number="BC-175975"),
        Wire(color="BROWN/YELLOW", gauge=16, insulation_type="GPT", number="BC-175976"),
        Wire(color="PINK", gauge=16, insulation_type="GPT", number="BC-175977"),
        Wire(color="BLUE/BLACK", gauge=16, insulation_type="GPT", number="BC-175978"),
        Wire(color="BLUE/YELLOW", gauge=16, insulation_type="GPT", number="BC-175979"),
        Wire(color="BLUE/WHITE", gauge=16, insulation_type="GPT", number="BC-175980"),
        Wire(color="GREEN/WHITE", gauge=16, insulation_type="GPT", number="BC-175981"),
        Wire(color="RED/WHITE", gauge=16, insulation_type="GPT", number="BC-175982"),
        Wire(color="WHITE", gauge=16, insulation_type="GPT", number="BC-175983"),
        Wire(color="GRAY", gauge=16, insulation_type="GPT", number="BC-175985"),
        Wire(color="BLACK", gauge=14, insulation_type="GPT", number="BC-175989"),
        Wire(color="ORANGE", gauge=16, insulation_type="GPT", number="BC-175990"),
        Wire(color="BLUE/ORANGE", gauge=16, insulation_type="GPT", number="BC-175998"),
        Wire(color="RED/BLUE", gauge=16, insulation_type="GPT", number="BC-186522"),
        Wire(color="YELLOW/RED", gauge=16, insulation_type="GPT", number="BC-186526"),
        Wire(color="TAN/BLUE", gauge=16, insulation_type="GPT", number="BC-186527"),
        Wire(color="GREEN/YELLOW", gauge=16, insulation_type="GPT", number="BC-200906"),
        Wire(color="BROWN", gauge=12, insulation_type="GPT", number="BC-230075"),
        Wire(color="BROWN/ORANGE", gauge=12, insulation_type="GPT", number="BC-230076"),
        Wire(color="YELLOW", gauge=12, insulation_type="GPT", number="BC-230077"),
        Wire(color="ORANGE/GREEN", gauge=16, insulation_type="GPT", number="BC-230078"),
        Wire(color="BLACK/YELLOW", gauge=16, insulation_type="GPT", number="BC-230079"),
        Wire(color="PINK/RED", gauge=14, insulation_type="GPT", number="BC-230080"),
        Wire(color="PINK/RED", gauge=12, insulation_type="GPT", number="BC-230081"),
        Wire(color="RED", gauge=4, insulation_type="GPT", number="BC-236730"),
        Wire(color="GREEN/BLACK", gauge=16, insulation_type="GPT", number="BC-248254"),
        Wire(color="ORANGE", gauge=14, insulation_type="GPT", number="BC-248255"),
        Wire(color="ORANGE/BLACK", gauge=16, insulation_type="GPT", number="BC-249430"),
        Wire(color="RED", gauge=12, insulation_type="GPT", number="BC-700005"),
        Wire(color="GRAY", gauge=18, insulation_type="GPT", number="BC-700016"),
        Wire(color="BLACK", gauge=18, insulation_type="GPT", number="BC-700017"),
        Wire(color="BLACK/WHITE", gauge=18, insulation_type="GPT", number="BC-700018"),
        Wire(color="TAN/BLACK", gauge=16, insulation_type="GPT", number="BC-700058"),
        Wire(color="BLUE/GRAY", gauge=16, insulation_type="GPT", number="BC-700059"),
        Wire(color="BROWN/RED", gauge=14, insulation_type="GPT", number="BC-700081"),
        Wire(color="BLUE/RED", gauge=16, insulation_type="GPT", number="BC-700082"),
        Wire(color="YELLOW", gauge=10, insulation_type="GPT", number="BC-700090"),
        Wire(color="YELLOW", gauge=4, insulation_type="GPT", number="BC-700094"),
        Wire(color="ORANGE", gauge=10, insulation_type="GPT", number="BC-700097"),
        Wire(color="BLACK/PINK", gauge=16, insulation_type="GPT", number="BC-700098"),
        Wire(color="WHITE", gauge=12, insulation_type="GPT", number="BC-700105"),
        Wire(color="BLUE", gauge=18, insulation_type="GPT", number="BC-700015"),
        Wire(color="BROWN/RED", gauge=16, insulation_type="GPT", number="BC-175955"),
        Wire(color="RED/PURPLE", gauge=16, insulation_type="GPT", number="BC-175939"),
        Wire(color="YELLOW", gauge=16, insulation_type="GPT", number="BC-700091"),
        Wire(color="WHITE/RED", gauge=12, insulation_type="GPT", number="BC-248246"),
        Wire(color="BLACK/RED", gauge=14, insulation_type="GPT", number="BC-248252"),
        Wire(color="WHITE/RED", gauge=14, insulation_type="GPT", number="BC-248250"),
        Wire(color="BLACK/RED", gauge=12, insulation_type="GPT", number="BC-248248"),
        Wire(color="WHITE/GREEN", gauge=12, insulation_type="GPT", number="BC-248247"),
        Wire(color="WHITE/GREEN", gauge=14, insulation_type="GPT", number="BC-248251"),
        Wire(color="BLACK/GREEN", gauge=12, insulation_type="GPT", number="BC-248249"),
        Wire(color="BLACK/GREEN", gauge=14, insulation_type="GPT", number="BC-248253"),
        Wire(color="GRAY/BLACK", gauge=18, insulation_type="GPT", number="BC-175994"),
        Wire(color="YELLOW/BROWN", gauge=12, insulation_type="GPT", number="BC-700122"),
        Wire(color="BROWN/GREEN", gauge=14, insulation_type="GPT", number="BC-700130"),
        Wire(color="BROWN/YELLOW", gauge=14, insulation_type="GPT", number="BC-175997"),
        Wire(color="RED/BLACK", gauge=12, insulation_type="GPT", number="BC-175968"),
        Wire(color="GREEN", gauge=18, insulation_type="GPT", number="BC-175937"),
        Wire(color="WHITE", gauge=18, insulation_type="GPT", number="BC-700132"),
        Wire(color="YELLOW/BROWN", gauge=14, insulation_type="GPT", number="BC-201152"),
        Wire(color="RED/ORANGE", gauge=16, insulation_type="GPT", number="BC-1000000"),
        Wire(
            color="YELLOW/BLACK", gauge=16, insulation_type="GPT", number="BC-1000001"
        ),
        Wire(color="WHITE/BLACK", gauge=16, insulation_type="GPT", number="BC-1000002"),
        Wire(
            color="PURPLE/BLACK", gauge=16, insulation_type="GPT", number="BC-1000003"
        ),
        Wire(color="BROWN", gauge=16, insulation_type="GPT", number="BC-1000004"),
        Wire(color="RED/BLACK", gauge=16, insulation_type="GPT", number="BC-1000005"),
        Wire(color="ORANGE/BLUE", gauge=16, insulation_type="GPT", number="BC-1000006"),
        Wire(color="ORANGE/GRAY", gauge=16, insulation_type="GPT", number="BC-1000007"),
        Wire(
            color="ORANGE/WHITE", gauge=16, insulation_type="GPT", number="BC-1000008"
        ),
        Wire(
            color="ORANGE/BROWN", gauge=16, insulation_type="GPT", number="BC-1000009"
        ),
        Wire(color="ORANGE/RED", gauge=16, insulation_type="GPT", number="BC-1000010"),
        Wire(
            color="ORANGE/YELLOW", gauge=16, insulation_type="GPT", number="BC-1000011"
        ),
        Wire(color="GRAY/WHITE", gauge=16, insulation_type="GPT", number="BC-1000012"),
        Wire(color="RED/BLUE", gauge=14, insulation_type="GPT", number="BC-1000013"),
        Wire(color="RED/BLACK", gauge=14, insulation_type="GPT", number="BC-1000014"),
        Wire(color="GREEN/BLUE", gauge=16, insulation_type="GXL", number="BC-1000015"),
        Wire(color="YEL/PUR", gauge=16, insulation_type="GXL", number="BC-1000016"),
        Wire(color="WHITE", gauge=14, insulation_type="GPT", number="BC-175960"),
        Wire(color="PURPLE", gauge=16, insulation_type="GPT", number="BC-175984A"),
        Wire(color="BLUE/WHITE", gauge=16, insulation_type="GXL", number="BC-1000019"),
        Wire(color="BROWN", gauge=16, insulation_type="GXL", number="BC-1000020"),
        Wire(color="BLACK", gauge=16, insulation_type="GXL", number="BC-1000021"),
        Wire(color="YELLOW", gauge=16, insulation_type="GXL", number="BC-1000022"),
        Wire(color="GREEN", gauge=16, insulation_type="GXL", number="BC-1000023"),
        Wire(color="GREEN/BLACK", gauge=16, insulation_type="GXL", number="BC-1000024"),
        Wire(color="GRN/WHITE", gauge=18, insulation_type="GXL", number="BC-1000025"),
        Wire(color="BLACK", gauge=18, insulation_type="GXL", number="BC-1000026"),
        Wire(color="RED/BLACK", gauge=18, insulation_type="GXL", number="BC-1000027"),
        Wire(color="BLACK", gauge=20, insulation_type="GXL", number="BC-1000028"),
        Wire(color="PURPLE", gauge=20, insulation_type="GXL", number="BC-1000029"),
        Wire(
            color="PURPLE/BLACK", gauge=20, insulation_type="GXL", number="BC-1000030"
        ),
        Wire(color="GREEN", gauge=20, insulation_type="GXL", number="BC-1000031"),
        Wire(color="WHITE", gauge=20, insulation_type="GXL", number="BC-1000047"),
        Wire(color="GRAY/WHITE", gauge=18, insulation_type="GXL", number="BC-1000053"),
        Wire(color="PINK", gauge=18, insulation_type="GXL", number="BC-1000055"),
        Wire(color="BLACK", gauge=12, insulation_type="GXL", number="BC-1000056"),
        Wire(color="BLACK", gauge=14, insulation_type="GXL", number="BC-1000057"),
        Wire(color="BROWN", gauge=18, insulation_type="GXL", number="BC-1000058"),
        Wire(color="RED/YELLOW", gauge=14, insulation_type="GXL", number="BC-1000059"),
        Wire(color="RED", gauge=12, insulation_type="GXL", number="BC-1000060"),
        Wire(color="WHITE", gauge=14, insulation_type="GXL", number="BC-1000061"),
        Wire(color="PURPLE", gauge=16, insulation_type="GXL", number="BC-1000062"),
        Wire(color="ORANGE", gauge=12, insulation_type="GXL", number="BC-1000063"),
        Wire(color="YELLOW", gauge=12, insulation_type="GXL", number="BC-1000064"),
        Wire(
            color="ORANGE/WHITE", gauge=12, insulation_type="GXL", number="BC-1000065"
        ),
        Wire(color="BROWN/BLACK", gauge=14, insulation_type="GXL", number="BC-1000066"),
        Wire(color="BROWN", gauge=14, insulation_type="GXL", number="BC-1000067"),
        Wire(color="ORANGE", gauge=18, insulation_type="GXL", number="BC-1000068"),
        Wire(color="WHITE", gauge=18, insulation_type="GXL", number="BC-1000069"),
        Wire(color="BLUE/WHITE", gauge=18, insulation_type="GXL", number="BC-1000072"),
        Wire(color="PINK", gauge=20, insulation_type="GXL", number="BC-1000073"),
        Wire(color="ORANGE", gauge=20, insulation_type="GXL", number="BC-1000074"),
        Wire(color="RED/YELLOW", gauge=20, insulation_type="GXL", number="BC-1000075"),
        Wire(color="GREY/WHITE", gauge=16, insulation_type="GXL", number="BC-1000080"),
        Wire(color="WHITE/BLACK", gauge=20, insulation_type="GXL", number="BC-1000081"),
        Wire(color="RED", gauge=14, insulation_type="GXL", number="BC-1000082"),
        Wire(
            color="ORANGE/BLACK", gauge=14, insulation_type="GXL", number="BC-1000083"
        ),
        Wire(color="ORANGE/RED", gauge=18, insulation_type="GXL", number="BC-1000085"),
        Wire(color="RED/BLACK", gauge=16, insulation_type="GXL", number="BC-1000086"),
        Wire(color="BLACK/WHITE", gauge=16, insulation_type="GXL", number="BC-1000087"),
        Wire(color="BLUE", gauge=14, insulation_type="GPT", number="BC-1000093"),
        Wire(color="GREEN", gauge=10, insulation_type="GPT", number="BC-1000097"),
        Wire(color="GRAY/BLUE", gauge=14, insulation_type="GPT", number="BC-1000099"),
        Wire(color="PURPLE/RED", gauge=16, insulation_type="GPT", number="BC-1000101"),
        Wire(color="BROWN/RED", gauge=12, insulation_type="GPT", number="BC-1000102"),
        Wire(color="WHITE/BLACK", gauge=16, insulation_type="GXL", number="BC-1000106"),
        Wire(color="PINK/RED", gauge=16, insulation_type="GPT", number="BC-1000107"),
        Wire(color="PINK/GREEN", gauge=16, insulation_type="GPT", number="BC-1000108"),
        Wire(color="PINK/BLUE", gauge=16, insulation_type="GPT", number="BC-1000109"),
        Wire(color="RED", gauge=2, insulation_type="GXL", number="BC-1000111"),
        Wire(color="BLACK", gauge=2, insulation_type="GXL", number="BC-1000112"),
        Wire(
            color="PURPLE/WHITE", gauge=16, insulation_type="GPT", number="BC-1000117"
        ),
        Wire(color="RED/WHITE", gauge=18, insulation_type="GXL", number="BC-1000119"),
        Wire(color="BLUE", gauge=8, insulation_type="GXL", number="BC-1000120"),
        Wire(color="BLUE/BLACK", gauge=14, insulation_type="GPT", number="BC-1000122"),
        Wire(color="RED/ORANGE", gauge=10, insulation_type="GPT", number="BC-1000123"),
        Wire(color="GRAY/BLACK", gauge=12, insulation_type="GPT", number="BC-1000124"),
        Wire(
            color="ORANGE/WHITE", gauge=12, insulation_type="GPT", number="BC-1000125"
        ),
        Wire(color="GRAY/BLACK", gauge=16, insulation_type="GXL", number="BC-1000126"),
        Wire(color="WHITE", gauge=16, insulation_type="GXL", number="BC-1000127"),
        Wire(color="RED/WHITE", gauge=16, insulation_type="GXL", number="BC-1000129"),
        Wire(color="BLUE", gauge=16, insulation_type="GXL", number="BC-1000130"),
        Wire(color="YELLOW", gauge=18, insulation_type="GXL", number="BC-1000132"),
        Wire(color="GRAY", gauge=18, insulation_type="GXL", number="bc-1000133"),
        Wire(color="RED/YELLOW", gauge=18, insulation_type="GXL", number="BC-1000134"),
        Wire(color="RED/BLUE", gauge=18, insulation_type="GXL", number="BC-1000135"),
        Wire(color="RED/GREEN", gauge=18, insulation_type="GXL", number="BC-1000137"),
        Wire(color="PURPLE", gauge=18, insulation_type="GXL", number="BC-1000140"),
        Wire(color="BLACK", gauge=10, insulation_type="GXL", number="BC-1000141"),
        Wire(color="PURPLE", gauge=12, insulation_type="GXL", number="BC-1000142"),
        Wire(color="GREEN", gauge=12, insulation_type="GXL", number="BC-1000143"),
        Wire(color="PINK", gauge=12, insulation_type="GXL", number="BC-1000144"),
        Wire(color="PINK/BLACK", gauge=12, insulation_type="GXL", number="BC-1000145"),
        Wire(color="PINK/WHITE", gauge=12, insulation_type="GXL", number="BC-1000146"),
        Wire(color="BLUE", gauge=12, insulation_type="GXL", number="BC-1000147"),
        Wire(color="RED/WHITE", gauge=12, insulation_type="GXL", number="BC-1000148"),
        Wire(color="GRAY", gauge=12, insulation_type="GXL", number="BC-1000149"),
        Wire(color="BLACK/WHITE", gauge=14, insulation_type="GXL", number="BC-1000150"),
        Wire(color="PINK", gauge=14, insulation_type="GXL", number="BC-1000151"),
        Wire(color="RED/BLUE", gauge=16, insulation_type="GXL", number="BC-1000152"),
        Wire(color="PINK", gauge=16, insulation_type="GXL", number="BC-1000154"),
        Wire(color="GRAY", gauge=16, insulation_type="GXL", number="BC-1000157"),
        Wire(color="RED", gauge=16, insulation_type="GPT", number="BC-1000161"),
        Wire(color="GREEN", gauge=14, insulation_type="GPT", number="BC-1000162"),
        Wire(color="GREEN/BLACK", gauge=14, insulation_type="GPT", number="BC-1000163"),
        Wire(color="PURPLE", gauge=14, insulation_type="GPT", number="BC-1000164"),
        Wire(
            color="PURPLE/BLACK", gauge=14, insulation_type="GPT", number="BC-1000165"
        ),
        Wire(color="GRAY", gauge=14, insulation_type="GPT", number="BC-1000166"),
        Wire(color="WHITE/BLACK", gauge=14, insulation_type="GPT", number="BC-1000168"),
        Wire(color="WHITE/BROWN", gauge=16, insulation_type="GPT", number="BC-1000169"),
        Wire(
            color="ORANGE/GREEN", gauge=14, insulation_type="GPT", number="BC-1000170"
        ),
        Wire(color="YELLOW", gauge=18, insulation_type="GPT", number="BC-1000173"),
        Wire(color="RED", gauge=18, insulation_type="GPT", number="BC-1000183"),
        Wire(color="YELLOW/RED", gauge=20, insulation_type="GXL", number="BC-1000185"),
        Wire(color="GREEN/RED", gauge=18, insulation_type="GXL", number="BC-1000187"),
        Wire(color="RED/BROWN", gauge=18, insulation_type="GXL", number="BC-1000188"),
        Wire(color="PINK/BLACK", gauge=18, insulation_type="GXL", number="BC-1000189"),
        Wire(color="GREEN", gauge=18, insulation_type="GXL", number="BC-1000190"),
        Wire(color="BLUE/BLACK", gauge=16, insulation_type="GXL", number="BC-1000192"),
        Wire(color="GRAY/WHITE", gauge=16, insulation_type="GXL", number="BC-1000194"),
        Wire(color="TAN/WHITE", gauge=16, insulation_type="GXL", number="BC-1000195"),
        Wire(color="TAN", gauge=16, insulation_type="GXL", number="BC-1000196"),
        Wire(color="TAN/BLACK", gauge=16, insulation_type="GXL", number="BC-1000197"),
        Wire(color="RED/ORANGE", gauge=16, insulation_type="GXL", number="BC-1000199"),
        Wire(
            color="BLACK/ORANGE", gauge=16, insulation_type="GXL", number="BC-1000200"
        ),
        Wire(
            color="PURPLE/BLACK", gauge=16, insulation_type="GXL", number="BC-1000201"
        ),
        Wire(color="BLUE", gauge=14, insulation_type="GXL", number="BC-1000202"),
        Wire(color="RED/WHITE", gauge=14, insulation_type="GXL", number="BC-1000203"),
        Wire(color="GREEN", gauge=14, insulation_type="GXL", number="BC-1000204"),
        Wire(color="BLUE/BLACK", gauge=14, insulation_type="GXL", number="BC-1000205"),
        Wire(color="YELLOW", gauge=14, insulation_type="GXL", number="BC-1000206"),
        Wire(color="TAN", gauge=14, insulation_type="GXL", number="BC-1000207"),
        Wire(color="BLACK/RED", gauge=14, insulation_type="GXL", number="BC-1000208"),
        Wire(color="RED/BLUE", gauge=12, insulation_type="GXL", number="BC-1000209"),
        Wire(color="RED", gauge=10, insulation_type="GXL", number="BC-1000210"),
        Wire(color="RED", gauge=20, insulation_type="GXL", number="BC-1000213"),
        Wire(color="BLACK/RED", gauge=16, insulation_type="GPT", number="BC-1000215"),
        Wire(color="BLACK/BLUE", gauge=16, insulation_type="GPT", number="BC-1000216"),
        Wire(color="ORANGE/RED", gauge=14, insulation_type="GPT", number="BC-1000217"),
        Wire(color="WHITE", gauge=10, insulation_type="GXL", number="BC-1000218"),
        Wire(color="BROWN/WHITE", gauge=14, insulation_type="GXL", number="bc-1000219"),
        Wire(color="BLUE/ORANGE", gauge=14, insulation_type="GPT", number="BC-1000220"),
        Wire(color="RED/GRAY", gauge=14, insulation_type="GPT", number="BC-1000221"),
        Wire(
            color="ORANGE/BLACK", gauge=14, insulation_type="GPT", number="BC-1000225"
        ),
        Wire(color="RED/YELLOW", gauge=16, insulation_type="GPT", number="BC-1000226"),
        Wire(
            color="WHITE/ORANGE", gauge=16, insulation_type="GPT", number="BC-1000227"
        ),
        Wire(color="WHITE", gauge=12, insulation_type="GXL", number="BC-1000232"),
        Wire(color="PINK", gauge=14, insulation_type="GPT", number="BC-1000234"),
        Wire(color="PINK", gauge=12, insulation_type="GPT", number="BC-1000237"),
        Wire(color="RED/BLUE", gauge=10, insulation_type="GPT", number="BC-1000238"),
        Wire(color="GRAY/BLUE", gauge=16, insulation_type="GPT", number="BC-175972A"),
        Wire(
            color="BROWN/BLACK", gauge=14, insulation_type="GPT", number="BC-1000078A"
        ),
        Wire(
            color="BROWN/BLACK", gauge=16, insulation_type="GPT", number="BC-1000077A"
        ),
        Wire(color="RED/BLACK", gauge=10, insulation_type="GPT", number="BC-1000090A"),
        Wire(color="GRAY/BLACK", gauge=14, insulation_type="GPT", number="BC-1000091A"),
        Wire(color="BLUE", gauge=10, insulation_type="GPT", number="BC-1000096A"),
        Wire(color="TAN", gauge=14, insulation_type="GPT", number="BC-1000098A"),
        Wire(color="GRAY/GREEN", gauge=14, insulation_type="GPT", number="BC-1000100A"),
        Wire(color="BLUE/GREEN", gauge=16, insulation_type="GPT", number="BC-1000103A"),
        Wire(
            color="BLACK/GREEN", gauge=16, insulation_type="GPT", number="BC-1000214A"
        ),
        Wire(
            color="ORANGE/GRAY", gauge=14, insulation_type="GPT", number="BC-1000223A"
        ),
        Wire(color="GRAY/BLACK", gauge=18, insulation_type="GXL", number="BC-1000088A"),
        Wire(color="BLACK", gauge=4, insulation_type="GPT", number="BC-236729A"),
        Wire(color="BLUE/YELLOW", gauge=16, insulation_type="GXL", number="BC-1000251"),
        Wire(color="WHITE/BLUE", gauge=14, insulation_type="GXL", number="BC-1000254"),
        Wire(
            color="WHITE/PURPLE", gauge=16, insulation_type="GXL", number="BC-1000255"
        ),
        Wire(color="BLACK", gauge=22, insulation_type="SILICONE", number="BC-1000259"),
        Wire(color="RED", gauge=22, insulation_type="SILICONE", number="BC-1000260"),
        Wire(
            color="GREEN/YELLOW",
            gauge=22,
            insulation_type="SILICONE",
            number="BC-1000261",
        ),
        Wire(
            color="WHITE/YELLOW", gauge=18, insulation_type="GXL", number="BC-1000262"
        ),
        Wire(color="RED/BLACK", gauge=12, insulation_type="GXL", number="BC-1000263"),
        Wire(color="BLACK/GREEN", gauge=18, insulation_type="GXL", number="BC-1000264"),
        Wire(color="BLACK/BLUE", gauge=18, insulation_type="GXL", number="BC-1000265"),
        Wire(color="RED/GREEN", gauge=16, insulation_type="GXL", number="BC-1000266"),
        Wire(color="BLACK/RED", gauge=18, insulation_type="GXL", number="BC-1000267"),
        Wire(
            color="GREEN/YELLOW", gauge=16, insulation_type="GXL", number="BC-1000268"
        ),
        Wire(color="YELLOW", gauge=8, insulation_type="GPT", number="BC-1000269"),
        Wire(color="GREEN/RED", gauge=16, insulation_type="GPT", number="BC-1000275"),
        Wire(
            color="PURPLE/YELLOW", gauge=16, insulation_type="GPT", number="BC-1000276"
        ),
        Wire(color="YELLOW", gauge=20, insulation_type="GXL", number="BC-1000277"),
        Wire(color="WHITE", gauge=8, insulation_type="GXL", number="BC-1000280"),
        Wire(color="BLUE", gauge=10, insulation_type="GXL", number="BC-1000281"),
        Wire(color="GRAY", gauge=14, insulation_type="GXL", number="BC-1000282"),
        Wire(
            color="YELLOW/WHITE", gauge=16, insulation_type="GXL", number="BC-1000283"
        ),
        Wire(color="PINK/WHITE", gauge=16, insulation_type="GXL", number="BC-1000284"),
        Wire(color="BROWN/BLACK", gauge=16, insulation_type="GXL", number="BC-1000285"),
        Wire(color="RED", gauge=8, insulation_type="GXL", number="BC-1000289"),
        Wire(
            color="YELLOW/BLACK", gauge=18, insulation_type="GXL", number="BC-1000290"
        ),
        Wire(
            color="YELLOW/BLACK", gauge=16, insulation_type="GXL", number="BC-1000291"
        ),
        Wire(color="ORANGE", gauge=14, insulation_type="GXL", number="BC-1000292"),
        Wire(
            color="YELLOW/WHITE", gauge=14, insulation_type="GXL", number="BC-1000293"
        ),
        Wire(
            color="ORANGE/PURPLE", gauge=14, insulation_type="GPT", number="BC-1000294"
        ),
        Wire(color="YELLOW/BLUE", gauge=16, insulation_type="GPT", number="BC-1000295"),
        Wire(color="ORANGE/TAN", gauge=16, insulation_type="GPT", number="BC-1000296"),
        Wire(color="BLACK/BLUE", gauge=14, insulation_type="GPT", number="BC-1000298"),
        Wire(color="GRAY/RED", gauge=16, insulation_type="GPT", number="BC-1000299"),
        Wire(color="GREEN", gauge=10, insulation_type="GXL", number="BC-1000300"),
        Wire(color="PURPLE", gauge=14, insulation_type="GXL", number="BC-1000301"),
        Wire(color="GREEN/WHITE", gauge=14, insulation_type="GXL", number="BC-1000302"),
        Wire(color="GRAY", gauge=12, insulation_type="GPT", number="BC-1000303"),
        Wire(color="BLUE/RED", gauge=14, insulation_type="GPT", number="BC-1000304"),
        Wire(color="BROWN/WHITE", gauge=14, insulation_type="GPT", number="BC-1000305"),
        Wire(color="RED", gauge=4, insulation_type="SGX", number="BC-1000306"),
        Wire(color="BLACK", gauge=4, insulation_type="SGX", number="BC-1000307"),
        Wire(color="BLUE/GREEN", gauge=14, insulation_type="GPT", number="BC-1000315"),
        Wire(
            color="BLACK/YELLOW", gauge=14, insulation_type="GPT", number="BC-1000316"
        ),
        Wire(color="BLUE/WHITE", gauge=14, insulation_type="GPT", number="BC-1000317"),
        Wire(color="GREEN/WHITE", gauge=14, insulation_type="GPT", number="BC-1000318"),
        Wire(
            color="PURPLE/WHITE", gauge=18, insulation_type="GXL", number="BC-1000319"
        ),
        Wire(color="GREEN/BLACK", gauge=18, insulation_type="GXL", number="BC-1000320"),
        Wire(color="GREEN/BLACK", gauge=10, insulation_type="GXL", number="BC-1000321"),
        Wire(color="ORANGE", gauge=10, insulation_type="GXL", number="BC-1000322"),
        Wire(color="RED", gauge=6, insulation_type="GXL", number="BC-1000323"),
        Wire(
            color="YELLOW/GREEN", gauge=16, insulation_type="GPT", number="BC-1000324"
        ),
        Wire(color="RED/PINK", gauge=16, insulation_type="GPT", number="BC-1000325"),
        Wire(color="ORANGE/PINK", gauge=16, insulation_type="GPT", number="BC-1000326"),
        Wire(color="RED/ORANGE", gauge=14, insulation_type="GPT", number="BC-1000327"),
        Wire(color="RED", gauge=1, insulation_type="GXL", number="BC-1000328"),
        Wire(color="BLACK", gauge=1, insulation_type="GXL", number="BC-1000329"),
        Wire(color="BLACK/RED", gauge=10, insulation_type="GPT", number="BC-1000331"),
        Wire(color="YELLOW/RED", gauge=14, insulation_type="GPT", number="BC-1000333"),
        Wire(color="BROWN", gauge=10, insulation_type="GPT", number="BC-1000334"),
        Wire(color="BROWN/GREEN", gauge=16, insulation_type="GPT", number="BC-1000335"),
        Wire(color="BROWN/RED", gauge=10, insulation_type="GPT", number="BC-1000336"),
        Wire(color="BROWN/BLUE", gauge=16, insulation_type="GPT", number="BC-1000337"),
        Wire(color="PINK/WHITE", gauge=16, insulation_type="GPT", number="BC-1000338"),
        Wire(color="BLACK/WHITE", gauge=16, insulation_type="GPT", number="BC-1000339"),
        Wire(color="WHITE/RED", gauge=16, insulation_type="GPT", number="BC-1000340"),
        Wire(color="RED/GREEN", gauge=16, insulation_type="GPT", number="BC-1000341"),
        Wire(
            color="PURPLE/WHITE", gauge=14, insulation_type="GPT", number="BC-1000342"
        ),
        Wire(color="PURPLE/RED", gauge=12, insulation_type="GPT", number="BC-1000343"),
        Wire(color="TAN/GREEN", gauge=16, insulation_type="GPT", number="BC-1000344"),
        Wire(color="TAN/RED", gauge=16, insulation_type="GPT", number="BC-1000345"),
        Wire(color="WHITE/GREEN", gauge=16, insulation_type="GPT", number="BC-1000346"),
        Wire(color="WHITE/BLUE", gauge=16, insulation_type="GPT", number="BC-1000347"),
        Wire(
            color="BLACK/PURPLE", gauge=16, insulation_type="GPT", number="BC-1000348"
        ),
        Wire(
            color="BROWN/YELLOW", gauge=12, insulation_type="GPT", number="BC-1000349"
        ),
        Wire(
            color="BROWN/YELLOW", gauge=10, insulation_type="GPT", number="BC-1000350"
        ),
    ]

    with session_maker() as session:
        for terminal in terminals:
            if (
                session.query(Terminal)
                .filter_by(description=terminal.description)
                .first()
            ):
                continue
            session.add(terminal)
            session.commit()

        for wire in wires:
            if session.query(Wire).filter_by(number=wire.number).first():
                continue
            session.add(wire)
            session.commit()


def process_cut_sheet_row(
    session_maker,
    data: dict[str, str],
    customer_name: str = "",
    part_number: str = "",
    user: User = None,
) -> None:
    """
    Process a row from the cut sheet.

    :param data: The row of data from the cut sheet.
    """
    with session_maker() as session:
        color, gauge, insulation_type = data["Color"], data["Gauge"], data["Type"]
        wire = (
            session.query(Wire)
            .filter_by(color=color, gauge=gauge, insulation_type=insulation_type)
            .first()
        )
        if not wire:
            wire = Wire(
                color=color,
                gauge=gauge,
                insulation_type=insulation_type,
            )
            session.add(wire)
            session.commit()

        left_terminal = (
            session.query(Terminal).filter_by(description=data["Left Terminal"]).first()
        )
        if not left_terminal:
            left_terminal = Terminal(
                description=data["Left Terminal"],
                strip_length=data["Left Strip"],
                strip_gap=data["Left Gap"],
            )
            session.add(left_terminal)
            session.commit()

        right_terminal = (
            session.query(Terminal)
            .filter_by(description=data["Right Terminal"])
            .first()
        )
        if not right_terminal:
            right_terminal = Terminal(
                description=data["Right Terminal"],
                strip_length=data["Right Strip"],
                strip_gap=data["Right Gap"],
            )
            session.add(right_terminal)
            session.commit()

        article = (
            session.query(Article)
            .filter_by(
                part_number=part_number,
                wire_id=wire.id,
                length=data["Length"],
                quantity=data["Qty"],
                left_terminal_id=left_terminal.id,
                right_terminal_id=right_terminal.id,
            )
            .first()
        )
        if not article:
            article = Article(
                part_number=part_number,
                wire_id=wire.id,
                length=data["Length"],
                quantity=data["Qty"],
                left_terminal_id=left_terminal.id,
                right_terminal_id=right_terminal.id,
                apply_left_terminal=True,
                apply_right_terminal=True,
            )
            session.add(article)
            session.commit()


if __name__ == "__main__":
    from settings import DATABASE_FILE

    engine = create_engine(f"sqlite:///{DATABASE_FILE}")
    drop_tables(engine)
    create_tables(engine)

    Session = sessionmaker(bind=engine)
