import streamlit as st
import psycopg
import os
from databricks import sdk
from psycopg_pool import ConnectionPool

# Database connection setup
workspace_client = sdk.WorkspaceClient()
endpoint = os.getenv("PGENDPOINT", "")
connection_pool = None


class OAuthConnection(psycopg.Connection):
    """Connection subclass that auto-refreshes OAuth credentials."""

    @classmethod
    def connect(cls, conninfo="", **kwargs):
        credential = workspace_client.postgres.generate_database_credential(
            endpoint=endpoint
        )
        kwargs["password"] = credential.token
        return super().connect(conninfo, **kwargs)


def get_connection_pool():
    """Get or create the connection pool."""
    global connection_pool
    if connection_pool is None:
        conn_string = (
            f"dbname={os.getenv('PGDATABASE')} "
            f"user={os.getenv('PGUSER')} "
            f"host={os.getenv('PGHOST')} "
            f"port={os.getenv('PGPORT')} "
            f"sslmode={os.getenv('PGSSLMODE', 'require')} "
            f"application_name={os.getenv('PGAPPNAME')}"
        )
        connection_pool = ConnectionPool(
            conn_string, connection_class=OAuthConnection, min_size=2, max_size=10
        )
    return connection_pool


def get_connection():
    """Get a connection from the pool."""
    return get_connection_pool().connection()

def get_tickets():
    """Retrieve all support tickets from Lakebase."""

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT
                    ticket_id,
                    title,
                    status,
                    created_by,
                    created_at
                FROM public.tickets
                ORDER BY created_at DESC
            """)

            return cur.fetchall()

def create_ticket(title, created_by):
    """Create a new support ticket."""

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO public.tickets
                    (title, status, created_by)
                VALUES
                    (%s, %s, %s)
                RETURNING ticket_id
            """, (title.strip(), "open", created_by.strip()))

            ticket_id = cur.fetchone()[0]
            conn.commit()

            return ticket_id

def update_ticket_status(ticket_id, new_status):
    """Update the status of a support ticket."""

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                UPDATE public.tickets
                SET status = %s
                WHERE ticket_id = %s
            """, (new_status, ticket_id))

            conn.commit()

def get_ticket_messages(ticket_id):
    """Retrieve all messages for a ticket."""

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT
                    message_id,
                    message_text,
                    author,
                    created_at
                FROM public.ticket_messages
                WHERE ticket_id = %s
                ORDER BY created_at ASC
            """, (ticket_id,))

            return cur.fetchall()

def add_ticket_message(ticket_id, message_text, author):
    """Add a message to an existing support ticket."""

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO public.ticket_messages
                    (ticket_id, message_text, author)
                VALUES
                    (%s, %s, %s)
                RETURNING message_id
            """, (
                ticket_id,
                message_text.strip(),
                author.strip()
            ))

            message_id = cur.fetchone()[0]
            conn.commit()

            return message_id





@st.fragment
def display_tickets():
    st.subheader("Support Tickets")

    tickets = get_tickets()

    if not tickets:
        st.info("No support tickets found.")
        return

    # Create ticket options for the dropdown
    ticket_options = {
        f"#{ticket_id} — {title}": ticket_id
        for ticket_id, title, status, created_by, created_at in tickets
    }

    selected_label = st.selectbox(
        "Select a ticket to view its messages",
        options=list(ticket_options.keys())
    )

    selected_ticket_id = ticket_options[selected_label]

    # Find the selected ticket
    selected_ticket = next(
        ticket for ticket in tickets
        if ticket[0] == selected_ticket_id
    )

    ticket_id, title, status, created_by, created_at = selected_ticket

    st.markdown("---")

    # --------------------------------------------------
    # Ticket Details
    # --------------------------------------------------

    st.markdown(f"### #{ticket_id} — {title}")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.write(f"**Status:** {status}")

    with col2:
        st.write(f"**Created by:** {created_by}")

    with col3:
        st.write(
            f"**Created:** {created_at.strftime('%Y-%m-%d %H:%M')}"
        )

    # --------------------------------------------------
    # Update Ticket Status
    # --------------------------------------------------

    st.subheader("Update Status")

    status_options = [
        "open",
        "in_progress",
        "resolved"
    ]

    new_status = st.selectbox(
        "Ticket status",
        options=status_options,
        index=status_options.index(status),
        key=f"status_{ticket_id}"
    )

    if st.button(
        "Update Status",
        key=f"update_status_{ticket_id}",
        type="primary"
    ):

        if new_status == status:
            st.info("Ticket is already in this status.")

        else:
            update_ticket_status(
                ticket_id,
                new_status
            )

            st.success(
                f"Ticket #{ticket_id} updated to '{new_status}'."
            )

            st.rerun()

    st.markdown("---")

    # --------------------------------------------------
    # Messages
    # --------------------------------------------------

    st.subheader("Messages")

    messages = get_ticket_messages(selected_ticket_id)

    if not messages:
        st.info("No messages for this ticket.")
    else:
        for message_id, message_text, author, created_at in messages:

            st.markdown(f"**{author}**")

            st.write(message_text)

            st.caption(
                created_at.strftime("%Y-%m-%d %H:%M")
            )

            st.divider()

    # --------------------------------------------------
    # Add Message
    # --------------------------------------------------

    st.subheader("Add Message")

    with st.form(
        f"add_message_form_{selected_ticket_id}",
        clear_on_submit=True
    ):

        author = st.text_input(
            "Author",
            placeholder="Your name"
        )

        message_text = st.text_area(
            "Message",
            placeholder="Type your support message..."
        )

        submitted = st.form_submit_button(
            "Add Message",
            type="primary"
        )

        if submitted:

            if not author.strip() or not message_text.strip():

                st.error(
                    "Please enter both your name and message."
                )

            else:

                message_id = add_ticket_message(
                    selected_ticket_id,
                    message_text,
                    author
                )

                st.success(
                    f"Message #{message_id} added successfully!"
                )

                st.rerun()


# Streamlit UI
def main():
    st.set_page_config(
        page_title="SupportDesk",
        page_icon="🎫",
        layout="wide"
    )

    st.title("🎫 SupportDesk")
    st.caption("Internal Support Ticket Management")

    st.markdown("---")

    # Create New Ticket
    st.subheader("Create New Ticket")

    with st.form("create_ticket_form", clear_on_submit=True):

        title = st.text_input(
            "Ticket title",
            placeholder="Describe the support issue"
        )

        created_by = st.text_input(
            "Created by",
            placeholder="Your name"
        )

        submitted = st.form_submit_button(
            "Create Ticket",
            type="primary"
        )

        if submitted:

            if not title.strip() or not created_by.strip():
                st.error(
                    "Please enter both the ticket title and your name."
                )

            else:
                ticket_id = create_ticket(
                    title,
                    created_by
                )

                st.success(
                    f"Ticket #{ticket_id} created successfully!"
                )

                st.rerun()

    st.markdown("---")

    # Display existing tickets
    display_tickets()


if __name__ == "__main__":
    main()