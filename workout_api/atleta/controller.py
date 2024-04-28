from datetime import datetime
from sqlite3 import IntegrityError
from uuid import uuid4

from fastapi import APIRouter, Body, HTTPException, Query, status
from pydantic import UUID4
from sqlalchemy import select

from workout_api.atleta.models import AtletaModel
from workout_api.atleta.schemas import (AtletaIn, AtletaOut, AtletaReduzido,
                                        AtletaUpdate)
from workout_api.categorias.models import CategoriaModel
from workout_api.centro_treinamento.models import CentroTreinamentoModel
from workout_api.contrib.dependecies import DatabaseDependecy

router = APIRouter()


@router.post(
    path='/',
    summary='Criar um novo atleta',
    status_code=status.HTTP_201_CREATED,
    response_model=AtletaOut
)
async def post(
    db_session: DatabaseDependecy, atleta_in: AtletaIn = Body(...)
) -> AtletaOut:
    nome_categoria = atleta_in.categoria.nome
    nome_centro_treinamento = atleta_in.centro_treinamento.nome
    categoria = (await db_session
                 .execute(select(CategoriaModel)
                          .filter_by(nome=nome_categoria))
                 ).scalars().first()

    if not categoria:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Categoria {nome_categoria} não foi encontrada")
    centro_treinamento = (await db_session
                          .execute(select(CentroTreinamentoModel)
                                   .filter_by(nome=nome_centro_treinamento))
                          ).scalars().first()

    if not centro_treinamento:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Centro de treinamento {nome_centro_treinamento} não foi encontrado")
    try:
        atleta_out = AtletaOut(
            id=uuid4(), created_at=datetime.utcnow(), **atleta_in.model_dump())
        atleta_model = AtletaModel(
            **atleta_out.model_dump(exclude={'categoria', 'centro_treinamento'}))
        atleta_model.categoria_id = categoria.pk_id
        atleta_model.centro_treinamento_id = centro_treinamento.pk_id

        db_session.add(atleta_model)
        await db_session.commit()
    except IntegrityError:
        raise HTTPException(status_code=status.HTTP_303_SEE_OTHER,
                            detail=f"Já existe um atleta cadastrado com esse cpf: {atleta_in.cpf}")
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="Ocorreu um erro ao cadastrar o atleta")

    return atleta_out


@router.get(
    path='/',
    summary='Consultar todos os atletas',
    status_code=status.HTTP_200_OK,
    response_model=list[AtletaReduzido]
)
async def query(db_session: DatabaseDependecy,
                nome: str = Query(None),
                cpf: str = Query(None)) -> list[AtletaReduzido]:
    filters = []
    if nome:
        filters.append(AtletaModel.nome == nome)
    if cpf:
        filters.append(AtletaModel.cpf == cpf)
    try:
        atletas: list[AtletaReduzido] = (
            await db_session
            .execute(select(AtletaModel).filter(*filters))
        ).scalars().all()
        return [AtletaReduzido.model_validate(atleta) for atleta in atletas]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Não foi possível retornar os atletas: {e}"
        )


@router.get(
    path='/{id}',
    summary='Consultar um atleta pelo id',
    status_code=status.HTTP_200_OK,
    response_model=AtletaOut
)
async def get(id: UUID4, db_session: DatabaseDependecy) -> AtletaOut:
    atleta: AtletaOut = (
        await db_session
        .execute(select(AtletaModel).filter_by(id=id)
                 )).scalars().first()
    if not atleta:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Atleta não encontrado no id: {id}")
    return atleta


@router.patch(
    path='/{id}',
    summary='Editar um atleta pelo id',
    status_code=status.HTTP_200_OK,
    response_model=AtletaOut
)
async def patch(id: UUID4,
                db_session: DatabaseDependecy,
                atleta_up: AtletaUpdate = Body(...)) -> AtletaOut:
    atleta: AtletaOut = (
        await db_session
        .execute(select(AtletaModel).filter_by(id=id)
                 )).scalars().first()
    if not atleta:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Atleta não encontrado no id: {id}")
    atleta_update = atleta_up.model_dump(exclude_unset=True)
    for key, value in atleta_update.items():
        setattr(atleta, key, value)

    await db_session.commit()
    await db_session.refresh(atleta)

    return atleta


@router.delete(
    path='/{id}',
    summary='Deletar um atleta pelo id',
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete(id: UUID4, db_session: DatabaseDependecy) -> None:
    atleta: AtletaOut = (
        await db_session
        .execute(select(AtletaModel).filter_by(id=id)
                 )).scalars().first()
    if not atleta:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Atleta não encontrado no id: {id}")

    await db_session.delete(atleta)
    await db_session.commit()
