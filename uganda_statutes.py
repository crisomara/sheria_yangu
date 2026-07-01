"""
Uganda Statutes Knowledge Base — Sheria Yangu

Curated statutory provisions from key Ugandan Acts relevant to common
citizen legal documents. Text is summarised from official Uganda Law
Reform Commission publications.

Acts covered:
  1. Constitution of Uganda 1995 (as amended)
  2. Employment Act 2006 (Cap. 219)
  3. Landlord and Tenant Act 2022
  4. Land Act 1998 (Cap. 227)
  5. Police Act 2006 (Cap. 303)
  6. Contracts Act 2010
  7. Tier 4 Microfinance Institutions and Moneylenders Act 2016
  8. Human Rights Enforcement Act 2019
"""

STATUTE_DB = [

    # ── Constitutional Rights (apply to all document types) ───────────────

    {
        "act": "Constitution of Uganda 1995",
        "section": "Article 24",
        "title": "Respect for human dignity and protection from inhuman treatment",
        "text": (
            "No person shall be subjected to any form of torture, cruel, inhuman or "
            "degrading treatment or punishment."
        ),
        "tags": ["constitutional", "rights", "criminal", "police"],
    },
    {
        "act": "Constitution of Uganda 1995",
        "section": "Article 28",
        "title": "Right to a fair hearing",
        "text": (
            "In the determination of civil rights and obligations or any criminal charge, "
            "a person shall be entitled to a fair, speedy and public hearing before an "
            "independent and impartial court or tribunal established by law."
        ),
        "tags": ["constitutional", "rights", "court", "criminal"],
    },
    {
        "act": "Constitution of Uganda 1995",
        "section": "Article 23",
        "title": "Protection of personal liberty",
        "text": (
            "No person shall be deprived of personal liberty except in accordance with "
            "the law. A person who is arrested, restricted or detained shall be informed "
            "immediately, in a language they understand, of the reasons for the arrest, "
            "restriction or detention and of their right to a lawyer of their choice."
        ),
        "tags": ["constitutional", "rights", "police", "arrest", "criminal"],
    },
    {
        "act": "Constitution of Uganda 1995",
        "section": "Article 26",
        "title": "Protection from deprivation of property",
        "text": (
            "Every person has a right to own property either individually or in "
            "association with others. No person shall be compulsorily deprived of "
            "property or any interest in or right over property except where required "
            "for public use and subject to prompt payment of fair and adequate "
            "compensation."
        ),
        "tags": ["constitutional", "rights", "land", "property"],
    },

    # ── Employment Act 2006 ───────────────────────────────────────────────

    {
        "act": "Employment Act 2006",
        "section": "Section 58",
        "title": "Notice of termination of contract",
        "text": (
            "Either party to a contract of service may terminate the contract by giving "
            "notice. The minimum notice periods are: "
            "(a) 7 days, where the employee has been employed for less than 6 months; "
            "(b) 1 month, where the employee has been employed for 6 months to 3 years; "
            "(c) 2 months, where the employee has been employed for more than 3 years. "
            "Notice must be in writing. Payment in lieu of notice is permitted."
        ),
        "tags": ["employment", "labour", "termination"],
    },
    {
        "act": "Employment Act 2006",
        "section": "Section 64",
        "title": "Summary dismissal",
        "text": (
            "An employer may summarily dismiss an employee without notice or payment in "
            "lieu of notice only where the employee is guilty of gross misconduct. "
            "Gross misconduct includes wilful disobedience of lawful orders, dishonesty, "
            "or conduct fundamentally incompatible with the employment relationship. "
            "The employer must give the employee an opportunity to be heard before "
            "summary dismissal."
        ),
        "tags": ["employment", "labour", "termination"],
    },
    {
        "act": "Employment Act 2006",
        "section": "Section 41",
        "title": "Prohibition of forced labour",
        "text": (
            "No person shall be required to perform forced or compulsory labour. "
            "Any contractual clause requiring an employee to work excessive hours "
            "without compensation, or preventing an employee from terminating "
            "employment, may constitute forced labour under this Act."
        ),
        "tags": ["employment", "labour"],
    },
    {
        "act": "Employment Act 2006",
        "section": "Section 52",
        "title": "Annual leave entitlement",
        "text": (
            "Every employee who has completed 12 months of continuous service is "
            "entitled to not less than 21 working days of annual leave with full pay. "
            "Contractual terms may not reduce this statutory minimum."
        ),
        "tags": ["employment", "labour"],
    },
    {
        "act": "Employment Act 2006",
        "section": "Section 83",
        "title": "Unfair termination",
        "text": (
            "A termination is unfair if the employer fails to prove that the reason "
            "for termination is valid and that the employee was afforded an opportunity "
            "to respond to the allegations. The burden of proof lies with the employer. "
            "Remedies include reinstatement or compensation."
        ),
        "tags": ["employment", "labour", "termination"],
    },

    # ── Landlord and Tenant Act 2022 ──────────────────────────────────────

    {
        "act": "Landlord and Tenant Act 2022",
        "section": "Section 30",
        "title": "Notice to vacate",
        "text": (
            "A landlord shall not evict a tenant without a written notice. The minimum "
            "notice period is: (a) 7 days for a monthly tenancy; (b) 1 month for a "
            "quarterly tenancy; (c) 3 months for an annual tenancy. The notice must "
            "state the reason for the eviction and the date by which the tenant must vacate."
        ),
        "tags": ["tenancy", "landlord", "property"],
    },
    {
        "act": "Landlord and Tenant Act 2022",
        "section": "Section 47",
        "title": "Prohibited eviction practices",
        "text": (
            "A landlord shall not evict a tenant by: disconnecting utilities, removing "
            "doors or windows, using threats or violence, or entering the premises "
            "without reasonable notice. A tenant subjected to any of these practices "
            "may report the matter to the Rent Tribunal or police."
        ),
        "tags": ["tenancy", "landlord", "property"],
    },
    {
        "act": "Landlord and Tenant Act 2022",
        "section": "Section 19",
        "title": "Rent increases",
        "text": (
            "A landlord who wishes to increase rent must give the tenant written notice "
            "of not less than 60 days before the proposed increase takes effect. "
            "The tenant has the right to challenge an unreasonable increase before "
            "the Rent Tribunal."
        ),
        "tags": ["tenancy", "landlord", "property"],
    },

    # ── Land Act 1998 ─────────────────────────────────────────────────────

    {
        "act": "Land Act 1998",
        "section": "Section 3",
        "title": "Forms of tenure",
        "text": (
            "Land in Uganda may be held under the following systems: "
            "(a) Customary tenure; (b) Freehold tenure; (c) Mailo tenure; "
            "(d) Leasehold tenure. A person's rights under each system differ "
            "significantly with respect to sale, transfer, and inheritance."
        ),
        "tags": ["land", "property", "registration"],
    },
    {
        "act": "Land Act 1998",
        "section": "Section 59",
        "title": "Rights of lawful occupants",
        "text": (
            "A lawful occupant on registered land has the right to occupy and use "
            "the land. The registered owner may not evict a lawful occupant without "
            "following the procedure prescribed by the Land Act, which includes "
            "compensation or alternative land."
        ),
        "tags": ["land", "property"],
    },

    # ── Police Act 2006 ───────────────────────────────────────────────────

    {
        "act": "Police Act 2006",
        "section": "Section 24",
        "title": "Conditions of arrest without warrant",
        "text": (
            "A police officer may arrest a person without a warrant only where there "
            "is reasonable cause to believe the person has committed a felony, or where "
            "the person is found committing a cognisable offence. The police officer "
            "must inform the arrested person of the reason for arrest immediately."
        ),
        "tags": ["police", "arrest", "criminal"],
    },
    {
        "act": "Police Act 2006",
        "section": "Section 25",
        "title": "Duty to bring arrested person before court",
        "text": (
            "A person arrested by police must be brought before a court of law within "
            "48 hours of arrest, or as soon as practicable. Detention beyond 48 hours "
            "without being charged or brought before a court is unlawful."
        ),
        "tags": ["police", "arrest", "criminal", "rights"],
    },

    # ── Contracts Act 2010 ────────────────────────────────────────────────

    {
        "act": "Contracts Act 2010",
        "section": "Section 12",
        "title": "Unconscionable contracts",
        "text": (
            "A contract or a term in a contract is voidable at the option of the "
            "disadvantaged party if it was entered into in circumstances involving "
            "inequality of bargaining power such that the contract or term is "
            "unconscionable. Courts may refuse to enforce unconscionable terms."
        ),
        "tags": ["contract", "financial", "employment"],
    },
    {
        "act": "Contracts Act 2010",
        "section": "Section 45",
        "title": "Penalty clauses",
        "text": (
            "A clause in a contract requiring a party in breach to pay a sum as a "
            "penalty — rather than a genuine pre-estimate of loss — may be reduced "
            "or set aside by a court. Disproportionate penalty clauses are unenforceable."
        ),
        "tags": ["contract", "financial", "loan"],
    },

    # ── Tier 4 Microfinance / Moneylenders Act 2016 ───────────────────────

    {
        "act": "Tier 4 Microfinance Institutions and Moneylenders Act 2016",
        "section": "Section 78",
        "title": "Disclosure of loan terms",
        "text": (
            "Before disbursing a loan, a moneylender must provide the borrower with a "
            "written statement disclosing: the total amount of the loan; the interest "
            "rate expressed as an annual percentage; all fees and charges; the repayment "
            "schedule; and the consequences of default. Failure to disclose renders the "
            "loan agreement voidable at the borrower's option."
        ),
        "tags": ["financial", "loan"],
    },
]
