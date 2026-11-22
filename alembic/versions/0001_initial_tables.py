"""initial tables

Revision ID: 0001_initial
Revises: 
Create Date: 2026-11-22 19:30:00

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '0001_initial'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Users
    op.create_table(
        'users',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('username', sa.String(length=64), nullable=True),
        sa.Column('first_name', sa.String(length=128), nullable=False),
        sa.Column('last_name', sa.String(length=128), nullable=True),
        sa.Column('language_code', sa.String(length=8), nullable=False, server_default='uz'),
        sa.Column('is_admin', sa.Boolean(), nullable=False, server_default=sa.text('false')),
        sa.Column('is_banned', sa.Boolean(), nullable=False, server_default=sa.text('false')),
        sa.Column('last_active', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_users_username', 'users', ['username'])

    # Kingdoms
    op.create_table(
        'kingdoms',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.BigInteger(), nullable=False),
        sa.Column('name', sa.String(length=64), nullable=False),
        sa.Column('level', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('experience', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('trophies', sa.Integer(), nullable=False, server_default='1000'),
        sa.Column('shield_until', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id')
    )
    op.create_index('ix_kingdoms_name', 'kingdoms', ['name'])
    op.create_index('ix_kingdoms_trophies', 'kingdoms', ['trophies'])
    op.create_index('ix_kingdoms_trophies_level', 'kingdoms', ['trophies', 'level'])

    # Resources
    op.create_table(
        'resources',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('kingdom_id', sa.Integer(), nullable=False),
        sa.Column('gold', sa.BigInteger(), nullable=False, server_default='1000'),
        sa.Column('wood', sa.BigInteger(), nullable=False, server_default='1000'),
        sa.Column('iron', sa.BigInteger(), nullable=False, server_default='500'),
        sa.Column('food', sa.BigInteger(), nullable=False, server_default='1000'),
        sa.Column('max_capacity', sa.BigInteger(), nullable=False, server_default='5000'),
        sa.Column('last_collected_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['kingdom_id'], ['kingdoms.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('kingdom_id')
    )

    # Buildings
    op.create_table(
        'buildings',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('kingdom_id', sa.Integer(), nullable=False),
        sa.Column('building_type', sa.String(length=32), nullable=False),
        sa.Column('level', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('is_upgrading', sa.Boolean(), nullable=False, server_default=sa.text('false')),
        sa.Column('upgrade_finish_time', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['kingdom_id'], ['kingdoms.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('kingdom_id', 'building_type', name='uq_kingdom_building_type')
    )
    op.create_index('ix_buildings_kingdom_type', 'buildings', ['kingdom_id', 'building_type'])

    # Troops
    op.create_table(
        'troops',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('kingdom_id', sa.Integer(), nullable=False),
        sa.Column('troop_type', sa.String(length=32), nullable=False),
        sa.Column('count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['kingdom_id'], ['kingdoms.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('kingdom_id', 'troop_type', name='uq_kingdom_troop_type')
    )
    op.create_index('ix_troops_kingdom_type', 'troops', ['kingdom_id', 'troop_type'])

    # Clans
    op.create_table(
        'clans',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('name', sa.String(length=64), nullable=False),
        sa.Column('tag', sa.String(length=10), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('leader_id', sa.BigInteger(), nullable=False),
        sa.Column('level', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('trophies', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('treasury_gold', sa.BigInteger(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['leader_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name'),
        sa.UniqueConstraint('tag')
    )
    op.create_index('ix_clans_name', 'clans', ['name'])
    op.create_index('ix_clans_tag', 'clans', ['tag'])
    op.create_index('ix_clans_trophies', 'clans', ['trophies'])

    # Clan Members
    op.create_table(
        'clan_members',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('clan_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.BigInteger(), nullable=False),
        sa.Column('role', sa.String(length=32), nullable=False, server_default='member'),
        sa.Column('donated_gold', sa.BigInteger(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['clan_id'], ['clans.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id'),
        sa.UniqueConstraint('clan_id', 'user_id', name='uq_clan_user')
    )
    op.create_index('ix_clan_members_clan_role', 'clan_members', ['clan_id', 'role'])

    # Battles
    op.create_table(
        'battles',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('battle_type', sa.String(length=16), nullable=False, server_default='pve'),
        sa.Column('attacker_id', sa.BigInteger(), nullable=False),
        sa.Column('defender_id', sa.BigInteger(), nullable=True),
        sa.Column('npc_name', sa.String(length=64), nullable=True),
        sa.Column('winner_id', sa.BigInteger(), nullable=True),
        sa.Column('is_attacker_winner', sa.Boolean(), nullable=False, server_default=sa.text('false')),
        sa.Column('attacker_casualties', sa.JSON(), nullable=False),
        sa.Column('defender_casualties', sa.JSON(), nullable=False),
        sa.Column('loot_gold', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('loot_wood', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('loot_iron', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('loot_food', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('trophies_delta', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('rounds_log', sa.JSON(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['attacker_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['defender_id'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_battles_attacker_created', 'battles', ['attacker_id', 'created_at'])
    op.create_index('ix_battles_defender_created', 'battles', ['defender_id', 'created_at'])

    # Inventory
    op.create_table(
        'inventory',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.BigInteger(), nullable=False),
        sa.Column('name', sa.String(length=64), nullable=False),
        sa.Column('item_type', sa.String(length=32), nullable=False),
        sa.Column('rarity', sa.String(length=32), nullable=False, server_default='common'),
        sa.Column('attack_bonus', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('defense_bonus', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('is_equipped', sa.Boolean(), nullable=False, server_default=sa.text('false')),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_inventory_user_equipped', 'inventory', ['user_id', 'is_equipped'])

    # Missions
    op.create_table(
        'missions',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.BigInteger(), nullable=False),
        sa.Column('mission_key', sa.String(length=64), nullable=False),
        sa.Column('title', sa.String(length=128), nullable=False),
        sa.Column('description', sa.String(length=256), nullable=False),
        sa.Column('target_count', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('current_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('reward_gold', sa.Integer(), nullable=False, server_default='100'),
        sa.Column('reward_wood', sa.Integer(), nullable=False, server_default='100'),
        sa.Column('reward_iron', sa.Integer(), nullable=False, server_default='50'),
        sa.Column('is_completed', sa.Boolean(), nullable=False, server_default=sa.text('false')),
        sa.Column('is_claimed', sa.Boolean(), nullable=False, server_default=sa.text('false')),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'mission_key', name='uq_user_mission')
    )
    op.create_index('ix_missions_user_claimed', 'missions', ['user_id', 'is_claimed'])

    # Transactions (Audit & Idempotency)
    op.create_table(
        'transactions',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.BigInteger(), nullable=False),
        sa.Column('idempotency_key', sa.String(length=128), nullable=False),
        sa.Column('category', sa.String(length=64), nullable=False),
        sa.Column('gold_delta', sa.BigInteger(), nullable=False, server_default='0'),
        sa.Column('wood_delta', sa.BigInteger(), nullable=False, server_default='0'),
        sa.Column('iron_delta', sa.BigInteger(), nullable=False, server_default='0'),
        sa.Column('food_delta', sa.BigInteger(), nullable=False, server_default='0'),
        sa.Column('details', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('idempotency_key')
    )
    op.create_index('ix_transactions_idempotency', 'transactions', ['idempotency_key'])
    op.create_index('ix_transactions_user_cat', 'transactions', ['user_id', 'category'])

    # Achievements
    op.create_table(
        'achievements',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.BigInteger(), nullable=False),
        sa.Column('code', sa.String(length=64), nullable=False),
        sa.Column('title', sa.String(length=128), nullable=False),
        sa.Column('description', sa.String(length=256), nullable=False),
        sa.Column('reward_gold', sa.Integer(), nullable=False, server_default='500'),
        sa.Column('unlocked_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'code', name='uq_user_achievement_code')
    )
    op.create_index('ix_achievements_user_code', 'achievements', ['user_id', 'code'])


def downgrade() -> None:
    op.drop_table('achievements')
    op.drop_table('transactions')
    op.drop_table('missions')
    op.drop_table('inventory')
    op.drop_table('battles')
    op.drop_table('clan_members')
    op.drop_table('clans')
    op.drop_table('troops')
    op.drop_table('buildings')
    op.drop_table('resources')
    op.drop_table('kingdoms')
    op.drop_table('users')
