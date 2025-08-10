# api/alembic/versions/2024_12_16_1000-0001_initial_migration.py
"""Initial migration - create all tables

Revision ID: 0001
Revises: 
Create Date: 2024-12-16 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '0001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # --- ENUM definitions (idempotent) ---
    user_role_enum = postgresql.ENUM(
        'admin', 'moderator', 'helpdesk', 'freelancer', 'customer',
        name='userrole', create_type=False
    )
    user_status_enum = postgresql.ENUM(
        'active', 'inactive', 'suspended', 'banned',
        name='userstatus', create_type=False
    )
    project_status_enum = postgresql.ENUM(
        'draft', 'open', 'in_progress', 'completed', 'cancelled', 'closed',
        name='projectstatus', create_type=False
    )
    project_budget_type_enum = postgresql.ENUM(
        'fixed', 'hourly',
        name='projectbudgettype', create_type=False
    )
    project_complexity_enum = postgresql.ENUM(
        'simple', 'intermediate', 'complex',
        name='projectcomplexity', create_type=False
    )
    proposal_status_enum = postgresql.ENUM(
        'draft', 'pending', 'accepted', 'rejected', 'withdrawn',
        name='proposalstatus', create_type=False
    )
    contract_status_enum = postgresql.ENUM(
        'draft', 'active', 'paused', 'completed', 'cancelled', 'disputed',
        name='contractstatus', create_type=False
    )
    contract_type_enum = postgresql.ENUM(
        'fixed_price', 'hourly',
        name='contracttype', create_type=False
    )
    milestone_status_enum = postgresql.ENUM(
        'pending', 'funded', 'in_progress', 'submitted', 'approved', 'released', 'disputed',
        name='milestonestatus', create_type=False
    )
    transaction_type_enum = postgresql.ENUM(
        'fund', 'release', 'payout', 'refund', 'fee', 'escrow', 'withdrawal',
        name='transactiontype', create_type=False
    )
    transaction_status_enum = postgresql.ENUM(
        'pending', 'processing', 'success', 'failed', 'cancelled', 'refunded',
        name='transactionstatus', create_type=False
    )
    payment_provider_enum = postgresql.ENUM(
        'payoneer', 'stripe', 'paypal', 'bank_transfer', 'internal',
        name='paymentprovider', create_type=False
    )
    thread_type_enum = postgresql.ENUM(
        'project_discussion', 'contract_communication', 'support_ticket', 'dispute',
        name='threadtype', create_type=False
    )
    message_type_enum = postgresql.ENUM(
        'text', 'file', 'image', 'system',
        name='messagetype', create_type=False
    )
    notification_type_enum = postgresql.ENUM(
        'new_project_posted', 'project_updated', 'project_cancelled',
        'proposal_received', 'proposal_accepted', 'proposal_rejected',
        'contract_created', 'contract_signed', 'contract_started', 'contract_completed', 'contract_cancelled',
        'milestone_funded', 'milestone_submitted', 'milestone_approved', 'milestone_released', 'milestone_overdue',
        'payment_received', 'payment_released', 'payout_processed', 'payment_failed',
        'new_message', 'review_received',
        'account_verified', 'profile_updated', 'system_maintenance',
        name='notificationtype', create_type=False
    )
    notification_priority_enum = postgresql.ENUM(
        'low', 'normal', 'high', 'urgent',
        name='notificationpriority', create_type=False
    )

    # Create ENUM types safely (no-op if already exist)
    bind = op.get_bind()
    for e in [
        user_role_enum, user_status_enum, project_status_enum, project_budget_type_enum,
        project_complexity_enum, proposal_status_enum, contract_status_enum, contract_type_enum,
        milestone_status_enum, transaction_type_enum, transaction_status_enum, payment_provider_enum,
        thread_type_enum, message_type_enum, notification_type_enum, notification_priority_enum
    ]:
        e.create(bind, checkfirst=True)

    # --- Tables ---
    op.create_table('users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('password_hash', sa.String(length=255), nullable=True),
        sa.Column('google_sub', sa.String(length=255), nullable=True),
        sa.Column('google_email_verified', sa.Boolean(), nullable=True),
        sa.Column('role', user_role_enum, nullable=False),
        sa.Column('status', user_status_enum, nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('is_verified', sa.Boolean(), nullable=False),
        sa.Column('last_login_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('email_verified_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_google_sub'), 'users', ['google_sub'], unique=True)
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)

    op.create_table('user_profiles',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('display_name', sa.String(length=100), nullable=True),
        sa.Column('first_name', sa.String(length=50), nullable=True),
        sa.Column('last_name', sa.String(length=50), nullable=True),
        sa.Column('title', sa.String(length=200), nullable=True),
        sa.Column('bio', sa.Text(), nullable=True),
        sa.Column('skills', sa.JSON(), nullable=True),
        sa.Column('hourly_rate', sa.DECIMAL(precision=10, scale=2), nullable=True),
        sa.Column('currency', sa.String(length=3), nullable=False),
        sa.Column('country', sa.String(length=100), nullable=True),
        sa.Column('city', sa.String(length=100), nullable=True),
        sa.Column('timezone', sa.String(length=50), nullable=True),
        sa.Column('website', sa.String(length=500), nullable=True),
        sa.Column('linkedin_url', sa.String(length=500), nullable=True),
        sa.Column('github_url', sa.String(length=500), nullable=True),
        sa.Column('avatar_url', sa.String(length=500), nullable=True),
        sa.Column('cover_image_url', sa.String(length=500), nullable=True),
        sa.Column('total_earnings', sa.DECIMAL(precision=12, scale=2), nullable=False),
        sa.Column('completed_projects', sa.Integer(), nullable=False),
        sa.Column('average_rating', sa.DECIMAL(precision=3, scale=2), nullable=True),
        sa.Column('total_reviews', sa.Integer(), nullable=False),
        sa.Column('is_available', sa.Boolean(), nullable=False),
        sa.Column('is_profile_public', sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id')
    )
    op.create_index(op.f('ix_user_profiles_id'), 'user_profiles', ['id'], unique=False)

    op.create_table('device_tokens',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('fcm_token', sa.String(length=500), nullable=False),
        sa.Column('platform', sa.String(length=20), nullable=False),
        sa.Column('device_id', sa.String(length=200), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('last_used_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('fcm_token')
    )
    op.create_index(op.f('ix_device_tokens_id'), 'device_tokens', ['id'], unique=False)

    op.create_table('projects',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('customer_id', sa.Integer(), nullable=False),
        sa.Column('budget_type', project_budget_type_enum, nullable=False),
        sa.Column('budget_min', sa.DECIMAL(precision=10, scale=2), nullable=True),
        sa.Column('budget_max', sa.DECIMAL(precision=10, scale=2), nullable=True),
        sa.Column('hourly_rate_min', sa.DECIMAL(precision=8, scale=2), nullable=True),
        sa.Column('hourly_rate_max', sa.DECIMAL(precision=8, scale=2), nullable=True),
        sa.Column('currency', sa.String(length=3), nullable=False),
        sa.Column('complexity', project_complexity_enum, nullable=True),
        sa.Column('estimated_duration', sa.Integer(), nullable=True),
        sa.Column('deadline', sa.Date(), nullable=True),
        sa.Column('status', project_status_enum, nullable=False),
        sa.Column('category', sa.String(length=100), nullable=True),
        sa.Column('subcategory', sa.String(length=100), nullable=True),
        sa.Column('required_skills', sa.JSON(), nullable=True),
        sa.Column('is_featured', sa.Boolean(), nullable=False),
        sa.Column('allows_proposals', sa.Boolean(), nullable=False),
        sa.Column('max_proposals', sa.Integer(), nullable=False),
        sa.Column('attachments', sa.JSON(), nullable=True),
        sa.Column('slug', sa.String(length=250), nullable=True),
        sa.Column('tags', sa.JSON(), nullable=True),
        sa.Column('view_count', sa.Integer(), nullable=False),
        sa.Column('proposal_count', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['customer_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('slug')
    )
    op.create_index(op.f('ix_projects_id'), 'projects', ['id'], unique=False)
    op.create_index(op.f('ix_projects_slug'), 'projects', ['slug'], unique=False)
    op.create_index('ix_projects_status_created', 'projects', ['status', 'created_at'], unique=False)

    op.create_table('proposals',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('project_id', sa.Integer(), nullable=False),
        sa.Column('freelancer_id', sa.Integer(), nullable=False),
        sa.Column('cover_letter', sa.Text(), nullable=False),
        sa.Column('bid_amount', sa.DECIMAL(precision=10, scale=2), nullable=False),
        sa.Column('currency', sa.String(length=3), nullable=False),
        sa.Column('estimated_delivery_days', sa.Integer(), nullable=True),
        sa.Column('proposed_milestones', sa.JSON(), nullable=True),
        sa.Column('additional_services', sa.JSON(), nullable=True),
        sa.Column('status', proposal_status_enum, nullable=False),
        sa.Column('attachments', sa.JSON(), nullable=True),
        sa.Column('portfolio_items', sa.JSON(), nullable=True),
        sa.Column('questions_answers', sa.JSON(), nullable=True),
        sa.ForeignKeyConstraint(['freelancer_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_proposals_id'), 'proposals', ['id'], unique=False)
    op.create_index('ix_proposals_project_status', 'proposals', ['project_id', 'status'], unique=False)

    op.create_table('contracts',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('project_id', sa.Integer(), nullable=False),
        sa.Column('customer_id', sa.Integer(), nullable=False),
        sa.Column('freelancer_id', sa.Integer(), nullable=False),
        sa.Column('winning_proposal_id', sa.Integer(), nullable=True),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('contract_type', contract_type_enum, nullable=False),
        sa.Column('total_amount', sa.DECIMAL(precision=10, scale=2), nullable=False),
        sa.Column('currency', sa.String(length=3), nullable=False),
        sa.Column('hourly_rate', sa.DECIMAL(precision=8, scale=2), nullable=True),
        sa.Column('start_date', sa.Date(), nullable=True),
        sa.Column('end_date', sa.Date(), nullable=True),
        sa.Column('estimated_hours', sa.Integer(), nullable=True),
        sa.Column('status', contract_status_enum, nullable=False),
        sa.Column('terms', sa.JSON(), nullable=True),
        sa.Column('deliverables', sa.JSON(), nullable=True),
        sa.Column('payment_schedule', sa.JSON(), nullable=True),
        sa.Column('approved_hours', sa.DECIMAL(precision=8, scale=2), nullable=False),
        sa.Column('billed_amount', sa.DECIMAL(precision=10, scale=2), nullable=False),
        sa.Column('paid_amount', sa.DECIMAL(precision=10, scale=2), nullable=False),
        sa.Column('signed_by_customer_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('signed_by_freelancer_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['customer_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['freelancer_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ),
        sa.ForeignKeyConstraint(['winning_proposal_id'], ['proposals.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_contracts_id'), 'contracts', ['id'], unique=False)

    op.create_table('milestones',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('contract_id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('order_index', sa.Integer(), nullable=False),
        sa.Column('amount', sa.DECIMAL(precision=10, scale=2), nullable=False),
        sa.Column('currency', sa.String(length=3), nullable=False),
        sa.Column('due_date', sa.Date(), nullable=True),
        sa.Column('estimated_hours', sa.Integer(), nullable=True),
        sa.Column('status', milestone_status_enum, nullable=False),
        sa.Column('funded_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('submitted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('approved_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('released_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('deliverable_url', sa.String(length=500), nullable=True),
        sa.Column('submission_notes', sa.Text(), nullable=True),
        sa.Column('approval_notes', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['contract_id'], ['contracts.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_milestones_id'), 'milestones', ['id'], unique=False)

    op.create_table('transactions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('contract_id', sa.Integer(), nullable=True),
        sa.Column('milestone_id', sa.Integer(), nullable=True),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('type', transaction_type_enum, nullable=False),
        sa.Column('amount', sa.DECIMAL(precision=10, scale=2), nullable=False),
        sa.Column('currency', sa.String(length=3), nullable=False),
        sa.Column('provider', payment_provider_enum, nullable=False),
        sa.Column('provider_transaction_id', sa.String(length=255), nullable=True),
        sa.Column('provider_reference', sa.String(length=255), nullable=True),
        sa.Column('status', transaction_status_enum, nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('metadata', sa.JSON(), nullable=True),
        sa.Column('platform_fee', sa.DECIMAL(precision=10, scale=2), nullable=False),
        sa.Column('payment_processor_fee', sa.DECIMAL(precision=10, scale=2), nullable=False),
        sa.Column('net_amount', sa.DECIMAL(precision=10, scale=2), nullable=False),
        sa.Column('initiated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('processed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('error_code', sa.String(length=50), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('retry_count', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['contract_id'], ['contracts.id'], ),
        sa.ForeignKeyConstraint(['milestone_id'], ['milestones.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_transactions_id'), 'transactions', ['id'], unique=False)

    op.create_table('threads',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('project_id', sa.Integer(), nullable=True),
        sa.Column('contract_id', sa.Integer(), nullable=True),
        sa.Column('type', thread_type_enum, nullable=False),
        sa.Column('title', sa.String(length=200), nullable=True),
        sa.Column('participants', sa.JSON(), nullable=False),
        sa.Column('is_archived', sa.Boolean(), nullable=False),
        sa.Column('last_message_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('message_count', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['contract_id'], ['contracts.id'], ),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_threads_id'), 'threads', ['id'], unique=False)

    op.create_table('messages',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('thread_id', sa.Integer(), nullable=False),
        sa.Column('sender_id', sa.Integer(), nullable=False),
        sa.Column('type', message_type_enum, nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('attachments', sa.JSON(), nullable=True),
        sa.Column('is_edited', sa.Boolean(), nullable=False),
        sa.Column('edited_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('is_system_message', sa.Boolean(), nullable=False),
        sa.Column('read_by', sa.JSON(), nullable=True),
        sa.Column('reply_to_message_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['reply_to_message_id'], ['messages.id'], ),
        sa.ForeignKeyConstraint(['sender_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['thread_id'], ['threads.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_messages_id'), 'messages', ['id'], unique=False)

    op.create_table('notifications',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('type', notification_type_enum, nullable=False),
        sa.Column('priority', notification_priority_enum, nullable=False),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('payload', sa.JSON(), nullable=True),
        sa.Column('is_read', sa.Boolean(), nullable=False),
        sa.Column('is_sent_push', sa.Boolean(), nullable=False),
        sa.Column('is_sent_email', sa.Boolean(), nullable=False),
        sa.Column('read_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('sent_push_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('sent_email_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_notifications_id'), 'notifications', ['id'], unique=False)
    op.create_index('ix_notifications_user_seen', 'notifications', ['user_id', 'is_read'], unique=False)

    op.create_table('reviews',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('contract_id', sa.Integer(), nullable=False),
        sa.Column('rater_id', sa.Integer(), nullable=False),
        sa.Column('ratee_id', sa.Integer(), nullable=False),
        sa.Column('overall_rating', sa.DECIMAL(precision=2, scale=1), nullable=False),
        sa.Column('communication_rating', sa.DECIMAL(precision=2, scale=1), nullable=True),
        sa.Column('quality_rating', sa.DECIMAL(precision=2, scale=1), nullable=True),
        sa.Column('timeliness_rating', sa.DECIMAL(precision=2, scale=1), nullable=True),
        sa.Column('professionalism_rating', sa.DECIMAL(precision=2, scale=1), nullable=True),
        sa.Column('title', sa.String(length=200), nullable=True),
        sa.Column('comment', sa.Text(), nullable=True),
        sa.Column('is_public', sa.Boolean(), nullable=False),
        sa.Column('is_verified', sa.Boolean(), nullable=False),
        sa.Column('skills_mentioned', sa.JSON(), nullable=True),
        sa.Column('tags', sa.JSON(), nullable=True),
        sa.Column('response', sa.Text(), nullable=True),
        sa.Column('response_created_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('is_flagged', sa.Boolean(), nullable=False),
        sa.Column('moderation_notes', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['contract_id'], ['contracts.id'], ),
        sa.ForeignKeyConstraint(['rater_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['ratee_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_reviews_id'), 'reviews', ['id'], unique=False)

    # --- Trigger function & triggers for updated_at ---
    op.execute("""
        CREATE OR REPLACE FUNCTION update_updated_at_column()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_at = CURRENT_TIMESTAMP;
            RETURN NEW;
        END;
        $$ language 'plpgsql';
    """)

    tables_with_updated_at = [
        'users', 'user_profiles', 'device_tokens', 'projects', 'proposals',
        'contracts', 'milestones', 'transactions', 'threads', 'messages',
        'notifications', 'reviews'
    ]

    for table in tables_with_updated_at:
        op.execute(f"""
            CREATE TRIGGER update_{table}_updated_at
            BEFORE UPDATE ON {table}
            FOR EACH ROW
            EXECUTE FUNCTION update_updated_at_column();
        """)


def downgrade() -> None:
    # Drop triggers first
    tables_with_updated_at = [
        'users', 'user_profiles', 'device_tokens', 'projects', 'proposals',
        'contracts', 'milestones', 'transactions', 'threads', 'messages',
        'notifications', 'reviews'
    ]
    for table in tables_with_updated_at:
        op.execute(f"DROP TRIGGER IF EXISTS update_{table}_updated_at ON {table};")

    # Drop the trigger function
    op.execute("DROP FUNCTION IF EXISTS update_updated_at_column();")

    # Drop custom indexes created explicitly (others drop with tables)
    op.drop_index('ix_messages_thread_created', table_name='messages')
    op.drop_index('ix_transactions_user_type', table_name='transactions')
    op.drop_index('ix_milestones_contract_status', table_name='milestones')
    op.drop_index('ix_contracts_freelancer_status', table_name='contracts')
    op.drop_index('ix_contracts_customer_status', table_name='contracts')
    op.drop_index('ix_proposals_freelancer_status', table_name='proposals')
    op.drop_index('ix_projects_customer_status', table_name='projects')

    # Drop all tables in reverse dependency order
    op.drop_table('reviews')
    op.drop_table('notifications')
    op.drop_table('messages')
    op.drop_table('threads')
    op.drop_table('transactions')
    op.drop_table('milestones')
    op.drop_table('contracts')
    op.drop_table('proposals')
    op.drop_table('projects')
    op.drop_table('device_tokens')
    op.drop_table('user_profiles')
    op.drop_table('users')

    # Drop ENUM types safely (reverse order)
    postgresql.ENUM(name='notificationpriority').drop(op.get_bind(), checkfirst=True)
    postgresql.ENUM(name='notificationtype').drop(op.get_bind(), checkfirst=True)
    postgresql.ENUM(name='messagetype').drop(op.get_bind(), checkfirst=True)
    postgresql.ENUM(name='threadtype').drop(op.get_bind(), checkfirst=True)
    postgresql.ENUM(name='paymentprovider').drop(op.get_bind(), checkfirst=True)
    postgresql.ENUM(name='transactionstatus').drop(op.get_bind(), checkfirst=True)
    postgresql.ENUM(name='transactiontype').drop(op.get_bind(), checkfirst=True)
    postgresql.ENUM(name='milestonestatus').drop(op.get_bind(), checkfirst=True)
    postgresql.ENUM(name='contracttype').drop(op.get_bind(), checkfirst=True)
    postgresql.ENUM(name='contractstatus').drop(op.get_bind(), checkfirst=True)
    postgresql.ENUM(name='proposalstatus').drop(op.get_bind(), checkfirst=True)
    postgresql.ENUM(name='projectcomplexity').drop(op.get_bind(), checkfirst=True)
    postgresql.ENUM(name='projectbudgettype').drop(op.get_bind(), checkfirst=True)
    postgresql.ENUM(name='projectstatus').drop(op.get_bind(), checkfirst=True)
    postgresql.ENUM(name='userstatus').drop(op.get_bind(), checkfirst=True)
    postgresql.ENUM(name='userrole').drop(op.get_bind(), checkfirst=True)
