from typing import Annotated, Optional

from pydantic import Field, PositiveFloat

from workout_api.categorias.schemas import CategoriaIn
from workout_api.centro_treinamento.schemas import CentroTreinamentoAtleta
from workout_api.contrib.schemas import BaseSchema, OutMixin


class Atleta(BaseSchema):
    nome: Annotated[str, Field(
        description="Nome do Atleta", example="Joao", max_length=50)]
    cpf: Annotated[str, Field(
        description="CPF do Atleta", example="12345678900", max_length=11)]
    idade: Annotated[int, Field(
        description="Idade do Atleta", example=20)]
    peso: Annotated[PositiveFloat, Field(
        description="Peso do Atleta", example=60.5)]
    altura: Annotated[PositiveFloat, Field(
        description="Altura do Atleta", example=1.59)]
    sexo: Annotated[str, Field(
        description="Sexo do Atleta", example="M", max_length=1)]
    categoria: Annotated[CategoriaIn, Field(description="Categoria do atleta")]
    centro_treinamento: Annotated[CentroTreinamentoAtleta, Field(
        description="Centro de treinamento do atleta")]


class AtletaIn(Atleta):
    pass


class AtletaOut(Atleta, OutMixin):
    pass


class AtletaUpdate(BaseSchema):
    nome: Annotated[Optional[str], Field(
        description="Nome do Atleta", example="Joao", max_length=50)]
    peso: Annotated[Optional[PositiveFloat], Field(
        description="Peso do Atleta", example=60.5)]


class AtletaReduzido(BaseSchema, OutMixin):
    nome: Annotated[str, Field(
        description="Nome do Atleta", example="Joao", max_length=50)]
    centro_treinamento: Annotated[CentroTreinamentoAtleta, Field(
        description="Centro de treinamento do atleta")]
    categoria: Annotated[CategoriaIn, Field(description="Categoria do atleta")]
