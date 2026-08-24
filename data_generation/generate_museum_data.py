"""Museum CRM Data Generator - Creates realistic museum operational data with intentional quality issues."""

import random
from datetime import datetime, timedelta
from faker import Faker
import psycopg2
from psycopg2.extras import execute_values

# Seed both generators for reproducible output
fake = Faker()
Faker.seed(42)
random.seed(42)

# Connection details matching the Docker container from Step 1
DB_CONFIG = {
    "dbname": "museum_crm",
    "user": "postgres",
    "password": <your_password>,
    "host": "localhost",
    "port": "5432",
}

# Valid values for categorical fields
MEMBERSHIP_STATUSES = ["active", "expired", "cancelled", "pending"]
MEMBERSHIP_TYPES = ["individual", "family", "student", "senior", "patron"]
TICKET_TYPES = ["general", "special_exhibit", "guided_tour", "family_pack", "school_group"]
CAMPAIGN_TYPES = ["email", "direct_mail", "social_media", "event", "phone"]
COMMUNICATION_PREFS = ["email", "mail", "phone", "sms", "none"]
COUPON_CODES = ["WELCOME10", "MEMBER20", "SUMMER15", "FAMILY25", "STUDENT10", None, None, None]
EXHIBITS = ["Impressionist Gallery", "Modern Art Wing", "Ancient Egypt", "Natural History", "Photography", "Sculpture Garden", "Children's Museum", "Rotating Exhibit"]


def create_schema_and_tables(conn):
    with conn.cursor() as cur:
        cur.execute("DROP SCHEMA IF EXISTS raw CASCADE;")
        cur.execute("CREATE SCHEMA raw;")
        cur.execute("""
            CREATE TABLE raw.raw_contacts (
                contact_id VARCHAR(50),
                first_name VARCHAR(100),
                last_name VARCHAR(100),
                email VARCHAR(200),
                phone VARCHAR(50),
                address_city VARCHAR(100),
                address_state VARCHAR(50),
                source VARCHAR(50),
                email_consent BOOLEAN,
                communication_preference VARCHAR(20),
                privacy_opt_out BOOLEAN,
                created_at TIMESTAMP,
                updated_at TIMESTAMP
            );
        """)
        cur.execute("""
            CREATE TABLE raw.raw_memberships (
                membership_id VARCHAR(50),
                contact_id VARCHAR(50),
                membership_type VARCHAR(50),
                status VARCHAR(50),
                start_date DATE,
                end_date DATE,
                renewal_count INTEGER,
                amount_paid NUMERIC(10, 2),
                payment_method VARCHAR(50),
                created_at TIMESTAMP
            );
        """)
        cur.execute("""
            CREATE TABLE raw.raw_donations (
                donation_id VARCHAR(50),
                contact_id VARCHAR(50),
                campaign_id VARCHAR(50),
                amount NUMERIC(10, 2),
                donation_date DATE,
                donation_type VARCHAR(50),
                is_recurring BOOLEAN,
                tax_receipt_sent BOOLEAN,
                created_at TIMESTAMP
            );
        """)
        cur.execute("""
            CREATE TABLE raw.raw_tickets (
                ticket_id VARCHAR(50),
                contact_id VARCHAR(50),
                ticket_type VARCHAR(50),
                quantity INTEGER,
                unit_price NUMERIC(10, 2),
                total_amount NUMERIC(10, 2),
                coupon_code VARCHAR(50),
                discount_amount NUMERIC(10, 2),
                purchase_date DATE,
                visit_date DATE,
                created_at TIMESTAMP
            );
        """)
        cur.execute("""
            CREATE TABLE raw.raw_campaigns (
                campaign_id VARCHAR(50),
                campaign_name VARCHAR(200),
                campaign_type VARCHAR(50),
                start_date DATE,
                end_date DATE,
                budget NUMERIC(10, 2),
                target_audience VARCHAR(100),
                status VARCHAR(50),
                created_at TIMESTAMP
            );
        """)
        cur.execute("""
            CREATE TABLE raw.raw_visits (
                visit_id VARCHAR(50),
                contact_id VARCHAR(50),
                visit_date DATE,
                exhibit_visited VARCHAR(200),
                duration_minutes INTEGER,
                is_member_visit BOOLEAN,
                party_size INTEGER,
                created_at TIMESTAMP
            );
        """)
    conn.commit()


def generate_contacts(n=500):
    contacts = []
    for i in range(n):
        contact_id = f"CTK-{i+1:05d}"
        created_at = fake.date_time_between(start_date="-2y", end_date="-6M")
        updated_at = fake.date_time_between(start_date=created_at, end_date="now")
        email = fake.email()
        email_consent = random.choice([True, True, True, False])
        communication_preference = random.choice(COMMUNICATION_PREFS)
        privacy_opt_out = random.choice([False, False, False, False, True])
        # Intentional quality issue: ~25 null emails
        if i >= 475:
            email = None
        contacts.append((
            contact_id, fake.first_name(), fake.last_name(), email,
            fake.phone_number() if random.random() > 0.1 else None,
            fake.city(), fake.state_abbr(),
            random.choice(["website", "front_desk", "event", "referral", "social_media"]),
            email_consent, communication_preference, privacy_opt_out, created_at, updated_at,
        ))
    return contacts


def generate_memberships(contacts, n=200):
    memberships = []
    member_contacts = random.sample(contacts, min(n, len(contacts)))
    for i, contact in enumerate(member_contacts):
        contact_id = contact[0]
        membership_id = f"MEM-{i+1:05d}"
        start_date = fake.date_between(start_date="-2y", end_date="-1M")
        end_date = start_date + timedelta(days=365)
        status = random.choice(MEMBERSHIP_STATUSES)
        membership_type = random.choice(MEMBERSHIP_TYPES)
        amount_map = {"individual": 75.00, "family": 150.00, "student": 40.00, "senior": 55.00, "patron": 500.00}
        amount = amount_map.get(membership_type, 75.00)
        # Intentional quality issue: ~10 invalid statuses
        if i >= 190:
            status = "pending_review"
        memberships.append((
            membership_id, contact_id, membership_type, status, start_date, end_date,
            random.randint(0, 5), amount, random.choice(["credit_card", "check", "cash", "online"]),
            fake.date_time_between(start_date=start_date, end_date=start_date + timedelta(days=1)),
        ))
    # Intentional quality issue: ~15 duplicate membership_ids
    for i in range(15):
        original = memberships[i]
        duplicate = (
            original[0], original[1], original[2], original[3], original[4], original[5],
            original[6] + 1, original[7], original[8],
            fake.date_time_between(start_date="-1M", end_date="now"),
        )
        memberships.append(duplicate)
    return memberships


def generate_donations(contacts, campaigns, n=300):
    donations = []
    donor_contacts = random.sample(contacts, min(n, len(contacts)))
    for i, contact in enumerate(donor_contacts):
        campaign = random.choice(campaigns) if random.random() > 0.3 else None
        donation_date = fake.date_between(start_date="-2y", end_date="today")
        donations.append((
            f"DON-{i+1:05d}", contact[0], campaign[0] if campaign else None,
            round(random.choice([25, 50, 100, 250, 500, 1000, 5000]) * random.uniform(0.8, 1.2), 2),
            donation_date, random.choice(["one_time", "recurring", "pledge", "in_kind"]),
            random.choice([True, False, False, False]), True,
            fake.date_time_between(start_date=donation_date, end_date=donation_date + timedelta(days=1)),
        ))
    return donations


def generate_campaigns(n=10):
    campaigns = []
    campaign_themes = [
        "Spring Membership Drive", "Year-End Giving", "Summer Family Fun",
        "New Exhibit Launch", "Donor Appreciation Gala", "Student Outreach",
        "Holiday Gift Memberships", "Corporate Partnership Push",
        "Anniversary Celebration", "Community Day Promotion",
    ]
    for i in range(n):
        start_date = fake.date_between(start_date="-18M", end_date="-1M")
        end_date = start_date + timedelta(days=random.randint(14, 90))
        campaigns.append((
            f"CMP-{i+1:05d}", campaign_themes[i], random.choice(CAMPAIGN_TYPES),
            start_date, end_date, round(random.uniform(500, 15000), 2),
            random.choice(["all_contacts", "lapsed_members", "donors", "visitors", "prospects"]),
            "completed" if end_date < datetime.now().date() else "active",
            fake.date_time_between(start_date=start_date - timedelta(days=7), end_date=start_date),
        ))
    return campaigns


def generate_tickets(contacts, n=800):
    tickets = []
    ticket_contacts = random.choices(contacts, k=n)
    for i, contact in enumerate(ticket_contacts):
        ticket_type = random.choice(TICKET_TYPES)
        quantity = random.randint(1, 6)
        price_map = {"general": 25.00, "special_exhibit": 35.00, "guided_tour": 45.00, "family_pack": 80.00, "school_group": 15.00}
        unit_price = price_map.get(ticket_type, 25.00)
        coupon = random.choice(COUPON_CODES)
        discount = 0.0
        if coupon:
            discount_pct = int("".join(filter(str.isdigit, coupon))) / 100
            discount = round(unit_price * quantity * discount_pct, 2)
        total = round(unit_price * quantity - discount, 2)
        purchase_date = fake.date_between(start_date="-1y", end_date="today")
        visit_date = purchase_date + timedelta(days=random.randint(0, 30))
        # Intentional quality issue: ~5 tickets with future purchase dates
        if i >= 795:
            purchase_date = fake.date_between(start_date="+1M", end_date="+6M")
            visit_date = purchase_date + timedelta(days=random.randint(0, 14))
        tickets.append((
            f"TKT-{i+1:05d}", contact[0], ticket_type, quantity, unit_price, total,
            coupon, discount, purchase_date, visit_date,
            fake.date_time_between(start_date=purchase_date, end_date=purchase_date + timedelta(days=1)),
        ))
    return tickets


def generate_visits(contacts, n=1000):
    visits = []
    visit_contacts = random.choices(contacts, k=n)
    for i, contact in enumerate(visit_contacts):
        visit_date = fake.date_between(start_date="-1y", end_date="today")
        visits.append((
            f"VIS-{i+1:05d}", contact[0], visit_date, random.choice(EXHIBITS),
            random.randint(30, 240), random.choice([True, False]), random.randint(1, 6),
            fake.date_time_between(start_date=visit_date, end_date=visit_date + timedelta(hours=12)),
        ))
    return visits


def load_data(conn, table, columns, data):
    with conn.cursor() as cur:
        sql = f"INSERT INTO raw.{table} ({', '.join(columns)}) VALUES %s"
        execute_values(cur, sql, data, page_size=100)
    conn.commit()
    print(f"  Loaded {len(data)} rows into raw.{table}")


def main():
    print("Connecting to museum_crm database...")
    conn = psycopg2.connect(**DB_CONFIG)
    print("Creating schema and tables...")
    create_schema_and_tables(conn)
    print("Generating data...")
    contacts = generate_contacts(500)
    campaigns = generate_campaigns(10)
    memberships = generate_memberships(contacts, 200)
    donations = generate_donations(contacts, campaigns, 300)
    tickets = generate_tickets(contacts, 800)
    visits = generate_visits(contacts, 1000)
    print("Loading data into PostgreSQL...")
    load_data(conn, "raw_contacts", ["contact_id", "first_name", "last_name", "email", "phone", "address_city", "address_state", "source", "email_consent", "communication_preference", "privacy_opt_out", "created_at", "updated_at"], contacts)
    load_data(conn, "raw_campaigns", ["campaign_id", "campaign_name", "campaign_type", "start_date", "end_date", "budget", "target_audience", "status", "created_at"], campaigns)
    load_data(conn, "raw_memberships", ["membership_id", "contact_id", "membership_type", "status", "start_date", "end_date", "renewal_count", "amount_paid", "payment_method", "created_at"], memberships)
    load_data(conn, "raw_donations", ["donation_id", "contact_id", "campaign_id", "amount", "donation_date", "donation_type", "is_recurring", "tax_receipt_sent", "created_at"], donations)
    load_data(conn, "raw_tickets", ["ticket_id", "contact_id", "ticket_type", "quantity", "unit_price", "total_amount", "coupon_code", "discount_amount", "purchase_date", "visit_date", "created_at"], tickets)
    load_data(conn, "raw_visits", ["visit_id", "contact_id", "visit_date", "exhibit_visited", "duration_minutes", "is_member_visit", "party_size", "created_at"], visits)
    conn.close()
    print("\nDone! Museum CRM data loaded successfully.")
    print("Quality issues injected: ~25 null emails, ~15 duplicate membership IDs,")
    print("~10 invalid statuses, ~5 future-dated tickets.")


if __name__ == "__main__":
    main()
