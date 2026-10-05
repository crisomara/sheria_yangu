"""
Uganda Statutes Knowledge Base — Sheria Yangu

Curated statutory provisions from key Ugandan Acts relevant to common
citizen legal documents. Text is summarised from official Uganda Law
Reform Commission publications.

Acts covered:
  1. Constitution of Uganda 1995 (as amended)
  2. Employment Act 2006 (Cap. 219)
  3. Landlord and Tenant Act 2022
  4. Contracts Act 2010
  5. Police (Amendment) Act 2006
  6. Land (Amendment) Act 2010
  7. Tier 4 Microfinance Institutions and Moneylenders Act 2016
"""

STATUTE_DB = [
    # ── Constitutional Rights (apply to all document types) ───────────────
    {
        "act": "Constitution of Uganda 1995",
        "section": "Article 24",
        "title": "Respect for human dignity and protection from inhuman treatment",
        "text": (
            "No person shall be subjected to any form of torture, cruel, inhuman or degrading treatment or punishment."
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
        "section": "Section 5",
        "title": "Forced labour",
        "text": (
            "(1) No person shall use or assist any other person, in using forced or compulsory labour. "
            "(2) The term “forced or compulsory labour “ does not include any work or service extracted "
            "by virtue of compulsory military service laws for work of a purely military character, "
            "or any work or service which forms part of the normal civic obligations of the citizens of Uganda."
        ),
        "tags": ["employment", "labour", "forced labour"],
    },
    {
        "act": "Employment Act 2006",
        "section": "Section 6",
        "title": "Discrimination in employment",
        "text": (
            "(3) Discrimination in employment shall be unlawful and includes any distinction, exclusion "
            "or preference made on the basis of race, colour, sex, religion, political opinion, "
            "national extraction or social origin, the HIV status or disability which has the effect "
            "of nullifying or impairing the treatment of a person in employment or occupation."
        ),
        "tags": ["employment", "discrimination", "equality"],
    },
    {
        "act": "Employment Act 2006",
        "section": "Section 7",
        "title": "Sexual harassment in employment",
        "text": (
            "(1) An employee shall be sexually harassed if an employer or representative makes a request "
            "for sexual activity that contains an implied or express promise of preferential treatment, "
            "uses language of a sexual nature, uses visual material of a sexual nature, or shows physical "
            "behaviour of a sexual nature which subjects the employee to unwelcome or offensive behaviour."
        ),
        "tags": ["employment", "harassment", "sexual harassment"],
    },
    {
        "act": "Employment Act 2006",
        "section": "Section 25",
        "title": "Oral and written contracts",
        "text": (
            "A contract of service, other than a contract which is required by this or any other Act "
            "to be in writing, may be made orally, and except as otherwise provided by this Act, "
            "shall apply equally to oral and written contracts."
        ),
        "tags": ["employment", "contracts", "legal"],
    },
    {
        "act": "Employment Act 2006",
        "section": "Section 32",
        "title": "Employment of Children",
        "text": (
            "(1) A child under the age of twelve years shall not be employed in any business, undertaking "
            "or work place. (2) A child under the age of fourteen years shall not be employed except "
            "for light work carried out under supervision of an adult aged over eighteen years, and "
            "which does not affect the child’s education."
        ),
        "tags": ["employment", "children", "child labour"],
    },
    {
        "act": "Employment Act 2006",
        "section": "Section 40",
        "title": "Duty of employer to provide work",
        "text": (
            "(1) Every employer shall provide his or her employee with work in accordance with the "
            "contract of service, during the period for which the contract is binding, and on the "
            "number of days equal to the number of working days expressly or impliedly provided for "
            "in the contract."
        ),
        "tags": ["employment", "employer duties", "wages"],
    },
    {
        "act": "Employment Act 2006",
        "section": "Section 41",
        "title": "Entitlement to wages",
        "text": (
            "(1) Subject to subsection (2), wages shall be paid in legal tender to the employee entitled "
            "to payment. (2) Notwithstanding subsection (1), an employer may, with the prior written "
            "agreement of the employee, pay wages by bank cheque, postal order, money order or by "
            "direct payment to the employee’s bank account."
        ),
        "tags": ["employment", "wages", "payment"],
    },
    {
        "act": "Employment Act 2006",
        "section": "Section 53",
        "title": "Length of working hours per week",
        "text": (
            "(1) Subject to subsections (2) and (3), in all establishments, the maximum working hours "
            "for employees shall be forty eight hours per week. (4) Hours of work shall not, except "
            "as provided in subsection (5), exceed ten hours per day or fifty six hours per week."
        ),
        "tags": ["employment", "working hours", "overtime"],
    },
    {
        "act": "Employment Act 2006",
        "section": "Section 54",
        "title": "Annual leave and public holidays",
        "text": (
            "(1) An employee shall be entitled to a holiday with full pay at the rate of seven days "
            "in respect of each period of a continuous four months’ service. (1)(b) An employee "
            "shall be entitled to a day’s holiday with full pay on every public holiday during "
            "his or her employment."
        ),
        "tags": ["employment", "leave", "holidays"],
    },
    {
        "act": "Employment Act 2006",
        "section": "Section 55",
        "title": "Sick pay",
        "text": (
            "(1) An employee who has completed not less than one month’s continuous service and "
            "is incapable of work because of sickness or injury is entitled to sick pay for the "
            "first month’s absence at full wages and every other benefit stipulated in the "
            "contract of service."
        ),
        "tags": ["employment", "sick leave", "benefits"],
    },
    {
        "act": "Employment Act 2006",
        "section": "Section 56",
        "title": "Maternity leave",
        "text": (
            "(1) A female employee shall, as a consequence of pregnancy, have the right to a period "
            "of sixty working days leave from work on full wages, of which at least four weeks "
            "shall follow the childbirth or miscarriage. (2) She shall have the right to return "
            "to the job which she held immediately before her maternity leave."
        ),
        "tags": ["employment", "maternity", "leave"],
    },
    {
        "act": "Employment Act 2006",
        "section": "Section 57",
        "title": "Paternity leave",
        "text": (
            "(1) A male employee shall, immediately after the delivery or miscarriage of a wife, "
            "have the right to a period of four working days’ leave from work yearly. (2) An "
            "employee referred to in subsection (1) shall be entitled to the payment of his full "
            "wages during the said paternity leave."
        ),
        "tags": ["employment", "paternity", "leave"],
    },
    {
        "act": "Employment Act 2006",
        "section": "Section 58",
        "title": "Notice periods",
        "text": (
            "(3) The notice required shall be: (a) not less than two weeks for service of 6 months "
            "to 1 year; (b) not less than one month for service of 1 to 5 years; (c) not less than "
            "two months for service of 5 to 10 years; and (d) not less than three months where "
            "the service is ten years or more."
        ),
        "tags": ["employment", "termination", "notice"],
    },
    {
        "act": "Employment Act 2006",
        "section": "Section 65",
        "title": "Termination",
        "text": (
            "(1) Termination shall be deemed to take place where: (a) the contract is ended by "
            "the employer with notice; (b) a fixed term contract expires and is not renewed; "
            "(c) the contract is ended by the employee without notice due to unreasonable conduct "
            "of the employer; or (d) the employee ends the contract in circumstances where they "
            "have received notice but end it before the expiry of the notice."
        ),
        "tags": ["employment", "termination", "dismissal"],
    },
    {
        "act": "Employment Act 2006",
        "section": "Section 69",
        "title": "Summary termination",
        "text": (
            "(1) Summary termination shall take place when an employer terminates the service of "
            "an employee without notice or with less notice than that to which the employee is "
            "entitled. (3) An employer is entitled to dismiss summarily where the employee has "
            "fundamentally broken his or her obligations arising under the contract of service."
        ),
        "tags": ["employment", "dismissal", "misconduct"],
    },
    # ── The Landlord and Tenant Act, 2022 ───────────────────────────────
    {
        "act": "The Landlord and Tenant Act, 2022",
        "section": "Section 3",
        "title": "Making of tenancy agreements",
        "text": (
            "(1) A tenancy agreement may be: (a) made in writing; (b) by word of mouth; "
            "(c) partly in writing and partly by word of mouth; (d) in the form of a data "
            "message; or (e) implied from the conduct of the parties."
        ),
        "tags": ["landlord", "tenant", "agreement"],
    },
    {
        "act": "The Landlord and Tenant Act, 2022",
        "section": "Section 4",
        "title": "Tenancy agreement of twenty five currency points or more to be in writing",
        "text": (
            "A tenancy agreement of the value of twenty five currency points or more shall "
            "not be enforceable by action unless— (a) the agreement is in writing or in form "
            "of a data message; or (b) the party against whom enforcement is sought admits "
            "that the agreement was entered into."
        ),
        "tags": ["landlord", "tenant", "legal"],
    },
    {
        "act": "The Landlord and Tenant Act, 2022",
        "section": "Section 6",
        "title": "Implied term as to fitness for human habitation",
        "text": (
            "(1) Where a tenancy is for the letting of residential premises there is implied— "
            "(a) a condition that the premises are fit for human habitation at the commencement "
            "of the tenancy; and (b) an undertaking that the exterior of the premises and common "
            "areas shall be kept by the landlord, fit for human habitation, during the tenancy."
        ),
        "tags": ["landlord", "habitation", "residential"],
    },
    {
        "act": "The Landlord and Tenant Act, 2022",
        "section": "Section 7",
        "title": "Duty to keep premises in repair",
        "text": (
            "(1) Subject to section 8, there is implied in every tenancy a term that the "
            "landlord shall keep the premises maintained in good repair save that the "
            "obligation shall extend to the exterior parts of the premises and common areas."
        ),
        "tags": ["landlord", "repair", "maintenance"],
    },
    {
        "act": "The Landlord and Tenant Act, 2022",
        "section": "Section 9",
        "title": "Circumstances where tenant may repair premises",
        "text": (
            "(1) A tenant may carry out repairs to the premises where— (a) the nature of the "
            "repairs required is urgent; or (b) the tenant has taken reasonable steps to "
            "arrange for the landlord to carry out repairs and the tenant is unable to get "
            "the landlord to carry out the repairs after serving fourteen days’ notice."
        ),
        "tags": ["tenant", "repair", "urgent"],
    },
    {
        "act": "The Landlord and Tenant Act, 2022",
        "section": "Section 10",
        "title": "Landlord responsible for taxes and rates",
        "text": (
            "(1) There is implied in every tenancy a term that the landlord is responsible "
            "for the payment of all taxes and rates imposed by law in respect of the premises."
        ),
        "tags": ["landlord", "taxes", "legal"],
    },
    {
        "act": "The Landlord and Tenant Act, 2022",
        "section": "Section 12",
        "title": "Utility charges for which tenant is liable",
        "text": (
            "(1) A tenant is liable for all charges in respect of the supply or use of "
            "electricity, gas, oil and similar services in respect of the tenant's "
            "occupation of rented premises that are separately metered."
        ),
        "tags": ["tenant", "utilities", "bills"],
    },
    {
        "act": "The Landlord and Tenant Act, 2022",
        "section": "Section 14",
        "title": "Tenant not to use premises for unlawful purpose",
        "text": (
            "A tenant shall not use the premises or permit the use of the rented premises for any unlawful purpose."
        ),
        "tags": ["tenant", "legal", "prohibition"],
    },
    {
        "act": "The Landlord and Tenant Act, 2022",
        "section": "Section 19",
        "title": "Landlord to ensure quiet enjoyment",
        "text": (
            "A landlord shall take all reasonable steps to ensure that the tenant has "
            "quiet enjoyment of the premises during the tenancy."
        ),
        "tags": ["landlord", "tenant rights", "privacy"],
    },
    {
        "act": "The Landlord and Tenant Act, 2022",
        "section": "Section 21",
        "title": "Tenant to pay rent",
        "text": (
            "(1) A tenant shall pay the rent on the date and in the manner agreed upon by "
            "the landlord and tenant. (2) The landlord shall issue a receipt upon payment "
            "of rent by the tenant."
        ),
        "tags": ["tenant", "rent", "payment"],
    },
    {
        "act": "The Landlord and Tenant Act, 2022",
        "section": "Section 24",
        "title": "Limit on rent in advance",
        "text": (
            "(1) Subject to subsection (2), a landlord shall not require a tenant— (a) in the "
            "case of tenancy of more than one month, to pay rent more than three months in "
            "advance; or (b) in a case of tenancy of less than one month, to pay rent more "
            "than two weeks in advance."
        ),
        "tags": ["landlord", "rent", "prepayment"],
    },
    {
        "act": "The Landlord and Tenant Act, 2022",
        "section": "Section 26",
        "title": "Increase of rent",
        "text": (
            "(1) Except where the parties otherwise agree, a landlord shall not increase "
            "rent at a rate of more than ten percent annually. (2) A landlord shall give a "
            "tenant at least sixty days’ notice, in the prescribed form, of a proposed "
            "increase in rent."
        ),
        "tags": ["landlord", "rent", "increase"],
    },
    {
        "act": "The Landlord and Tenant Act, 2022",
        "section": "Section 30",
        "title": "Security deposit",
        "text": (
            "(1) A landlord shall require a tenant to pay a security deposit for the "
            "purposes of securing the performance by the tenant of his or her obligations. "
            "(2) A landlord shall not require... an amount exceeding the rent payable for "
            "one month’s occupancy."
        ),
        "tags": ["landlord", "tenant", "security deposit"],
    },
    {
        "act": "The Landlord and Tenant Act, 2022",
        "section": "Section 38",
        "title": "Termination after notice",
        "text": (
            "(2) In a residential tenancy, notice of termination... shall be as follows— "
            "(a) in the case of a weekly tenancy; seven days’ notice; (b) in the case of "
            "a monthly tenancy; thirty days’ notice; and (c) in the case of a tenancy "
            "from year to year; sixty days’ notice."
        ),
        "tags": ["landlord", "tenant", "termination"],
    },
    {
        "act": "The Landlord and Tenant Act, 2022",
        "section": "Section 45",
        "title": "Unlawful eviction of tenant",
        "text": (
            "(1) A landlord shall not, except in accordance with this Act, or the terms "
            "of the tenancy agreement, evict a tenant from the premises. (2) Where a "
            "landlord evicts a tenant... in contravention of this Act... the tenant shall "
            "be entitled to... an equivalent to three months’ rent payable."
        ),
        "tags": ["landlord", "eviction", "remedy"],
    },
    # ── The Contracts Act, 2010 ───────────────────────────────────────────
    {
        "act": "The Contracts Act, 2010",
        "section": "Section 10",
        "title": "Agreement that amounts to a contract",
        "text": (
            "(1) A contract is an agreement made with the free consent of parties with "
            "capacity to contract, for a lawful consideration and with a lawful object, "
            "with the intention to be legally bound."
        ),
        "tags": ["contract", "legal", "agreement"],
    },
    {
        "act": "The Contracts Act, 2010",
        "section": "Section 11",
        "title": "Capacity to contract",
        "text": (
            "(1) A person has capacity to contract where that person is— (a) eighteen "
            "years or above; (b) of sound mind; and (c) not disqualified from contracting "
            "by any law to which he or she is subject."
        ),
        "tags": ["contract", "capacity", "legal"],
    },
    {
        "act": "The Contracts Act, 2010",
        "section": "Section 13",
        "title": "Free consent of parties to a contract",
        "text": (
            "Consent of parties to a contract is taken to be free where it is not caused "
            "by— (a) coercion; (b) undue influence; (c) fraud; (d) misrepresentation; or "
            "(e) mistake."
        ),
        "tags": ["contract", "consent", "validity"],
    },
    {
        "act": "The Contracts Act, 2010",
        "section": "Section 14",
        "title": "Undue influence",
        "text": (
            "(1) A contract is induced by undue influence where the relationship "
            "subsisting between the parties... is such that one of the parties is in "
            "a position to dominate the will of the other party and uses that position "
            "to obtain an unfair advantage."
        ),
        "tags": ["contract", "consent", "undue influence"],
    },
    {
        "act": "The Contracts Act, 2010",
        "section": "Section 15",
        "title": "Fraud",
        "text": (
            "(1) Consent is induced by fraud where any of the following acts is committed "
            "by a party... with intent of deceiving the other party... (a) a suggestion "
            "to a fact which is not true, made by a person who does not believe it to be true."
        ),
        "tags": ["contract", "consent", "fraud"],
    },
    {
        "act": "The Contracts Act, 2010",
        "section": "Section 19",
        "title": "Lawful consideration or objects",
        "text": (
            "(1) A consideration or an object of an agreement is lawful, except where "
            "the consideration or object— (a) is forbidden by law; (b) is of such nature "
            "that... it would defeat the provisions of any law; (c) is fraudulent; (d) "
            "involves... injury to a person or property; or (e) is declared immoral."
        ),
        "tags": ["contract", "consideration", "legality"],
    },
    {
        "act": "The Contracts Act, 2010",
        "section": "Section 23",
        "title": "Agreement void for uncertainty",
        "text": ("An agreement, the meaning of which is not certain or capable of being made certain, is void."),
        "tags": ["contract", "validity", "void"],
    },
    {
        "act": "The Contracts Act, 2010",
        "section": "Section 25",
        "title": "Agreement to do impossible act",
        "text": ("(1) An agreement to do an act which is impossible to perform is void."),
        "tags": ["contract", "performance", "void"],
    },
    {
        "act": "The Contracts Act, 2010",
        "section": "Section 33",
        "title": "Obligation of parties",
        "text": (
            "(1) The parties to a contract shall perform or offer to perform, their "
            "respective promises, unless the performance is dispensed with or excused "
            "under this Act or any other law."
        ),
        "tags": ["contract", "performance", "obligation"],
    },
    {
        "act": "The Contracts Act, 2010",
        "section": "Section 47",
        "title": "Failure to perform within a fixed time",
        "text": (
            "(1) Where a party... fails to do the thing at or before the specified time, "
            "the contract... becomes voidable at the option of the promisee, if the "
            "intention of the parties was that time was of the essence to the contract."
        ),
        "tags": ["contract", "performance", "time"],
    },
    {
        "act": "The Contracts Act, 2010",
        "section": "Section 51",
        "title": "Effect of novation, rescission and alteration of contract",
        "text": (
            "Where the parties to a contract agree to substitute for the original "
            "contract a new contract or to rescind or alter the original contract, the "
            "original contract need not be performed."
        ),
        "tags": ["contract", "performance", "alteration"],
    },
    {
        "act": "The Contracts Act, 2010",
        "section": "Section 61",
        "title": "Compensation for loss or damage caused by breach of contract",
        "text": (
            "(1) Where there is a breach of contract, the party who suffers the breach "
            "is entitled to receive from the party who breaches the contract, compensation "
            "for any loss or damage caused to him or her."
        ),
        "tags": ["contract", "breach", "remedy"],
    },
    {
        "act": "The Contracts Act, 2010",
        "section": "Section 64",
        "title": "Right to specific performance",
        "text": (
            "(1) Where a party to a contract is in breach, the other party may obtain "
            "an order of court requiring the party in breach to specifically perform "
            "his or her promise under the contract."
        ),
        "tags": ["contract", "breach", "specific performance"],
    },
    {
        "act": "The Contracts Act, 2010",
        "section": "Section 66",
        "title": "Discharge by frustration",
        "text": (
            "(1) Where a contract becomes impossible to perform or is frustrated and "
            "where a party cannot show that the other party assumed the risk of "
            "impossibility, the parties... shall be discharged from further performance."
        ),
        "tags": ["contract", "performance", "frustration"],
    },
    {
        "act": "The Contracts Act, 2010",
        "section": "Section 68",
        "title": "Interpretation for Part VIII (Indemnity and Guarantee)",
        "text": (
            "“contract of guarantee” means a contract to perform a promise or to "
            "discharge the liability of a third party in case of default... “contract of "
            "indemnity” means a contract by which one party promises to save the other "
            "party from loss caused to that other party."
        ),
        "tags": ["contract", "indemnity", "guarantee"],
    },
    # ── Police (Amendment) Act, 2006 ───────────────────────────────────────
    {
        "act": "Police (Amendment) Act, 2006",
        "section": "Section 2",
        "title": "Interpretation of 'arrestable offence'",
        "text": (
            "“arrestable offence” means an offence which on conviction may be punished "
            "by a term of imprisonment of one year or more, or a fine of not less than "
            "five currency points or both."
        ),
        "tags": ["police", "legal", "offence"],
    },
    {
        "act": "Police (Amendment) Act, 2006",
        "section": "Section 2",
        "title": "Interpretation of 'attested member'",
        "text": (
            "“attested member” means a police officer, regardless of rank, who has "
            "completed the training course, taken the requisite oath and been listed "
            "in the Force as a member."
        ),
        "tags": ["police", "membership", "legal"],
    },
    {
        "act": "Police (Amendment) Act, 2006",
        "section": "Section 4",
        "title": "Cooperation with civilian authorities",
        "text": (
            "Section 4 of the principal Act is amended... to co-operate with civilian "
            "authorities and other security organs established under the Constitution "
            "and with the population generally."
        ),
        "tags": ["police", "cooperation", "civilian"],
    },
    {
        "act": "Police (Amendment) Act, 2006",
        "section": "Section 11 (Inserting Section 13)",
        "title": "Delegation by the President of power of appointment",
        "text": (
            "(1) For the purposes of article 172 of the Constitution, the President may... "
            "delegate to the authorities specified... the powers necessary to enable "
            "those authorities to exercise the powers of appointment."
        ),
        "tags": ["police", "appointment", "presidential"],
    },
    {
        "act": "Police (Amendment) Act, 2006",
        "section": "Section 12",
        "title": "Pension qualification",
        "text": (
            "(5) A police officer shall qualify for pension on the attainment of forty "
            "five years of age if that officer has served for an uninterrupted period "
            "of at least ten years."
        ),
        "tags": ["police", "pension", "benefits"],
    },
    {
        "act": "Police (Amendment) Act, 2006",
        "section": "Section 13 (Inserting Section 17)",
        "title": "Resignation by police officers",
        "text": (
            "Subject to section 15, a police officer may not terminate his or her "
            "service with the force except on completion of a minimum of five years "
            "uninterrupted service, and with written permission."
        ),
        "tags": ["police", "resignation", "service"],
    },
    {
        "act": "Police (Amendment) Act, 2006",
        "section": "Section 14 (Inserting Section 20)",
        "title": "Employment of civilians",
        "text": (
            "(1) Civilians shall be employed in the police force in the following "
            "manner— (a) senior civilian established officers shall be appointed "
            "by the Public Service Commission on recommendation of the police authority."
        ),
        "tags": ["police", "employment", "civilians"],
    },
    {
        "act": "Police (Amendment) Act, 2006",
        "section": "Section 15",
        "title": "Obstruction of police officers",
        "text": (
            "(3) Any person who willfully obstructs or resists any police officer charged "
            "with the execution of his or her duty commits an offence and is liable... to "
            "imprisonment for a term not exceeding one year or both."
        ),
        "tags": ["police", "offence", "obstruction"],
    },
    {
        "act": "Police (Amendment) Act, 2006",
        "section": "Section 18 (Inserting Section 27A)",
        "title": "Procurement of information and attendance of witness",
        "text": (
            "(1) A police officer not below the rank of assistant inspector... may, in "
            "writing— (a) require the attendance before him or her of any person whom he "
            "or she has reason to believe has any knowledge which will assist in the "
            "investigation."
        ),
        "tags": ["police", "investigation", "witness"],
    },
    {
        "act": "Police (Amendment) Act, 2006",
        "section": "Section 18 (Inserting Section 27A, sub 3)",
        "title": "Offence for non-attendance of witness",
        "text": (
            "(3) Subject to subsection (4), where a person requested to attend... fails "
            "to attend as required... that person commits an offence and is liable... "
            "to imprisonment for a term not exceeding three months, or both."
        ),
        "tags": ["police", "offence", "witness"],
    },
    {
        "act": "Police (Amendment) Act, 2006",
        "section": "Section 20 (Inserting Section 47)",
        "title": "Summary dismissal power",
        "text": (
            "(3) The police authority shall have the power to dismiss summarily a police "
            "officer who has been prosecuted and convicted of a criminal offence."
        ),
        "tags": ["police", "dismissal", "disciplinary"],
    },
    {
        "act": "Police (Amendment) Act, 2006",
        "section": "Section 21",
        "title": "Force headquarters disciplinary court",
        "text": (
            "(a) force headquarters, which shall also serve as a disciplinary court "
            "for any police officer... for any disciplinary offence committed anywhere "
            "in Uganda."
        ),
        "tags": ["police", "disciplinary", "legal"],
    },
    {
        "act": "Police (Amendment) Act, 2006",
        "section": "Section 26 (Inserting Section 55A)",
        "title": "Appeals by prosecution",
        "text": (
            "The prosecution in a police disciplinary court may appeal against the "
            "decision of the court on the following grounds— (a) erroneous findings; "
            "or (b) a point of law."
        ),
        "tags": ["police", "legal", "appeals"],
    },
    {
        "act": "Police (Amendment) Act, 2006",
        "section": "Section 29 (Inserting Section 67A)",
        "title": "Integration of local administration police",
        "text": (
            "(1) The local administration police force in existence... shall be fully "
            "integrated into the police force as the local administration police."
        ),
        "tags": ["police", "local government", "integration"],
    },
    {
        "act": "Police (Amendment) Act, 2006",
        "section": "Section 31",
        "title": "Currency point value",
        "text": ("FIRST SCHEDULE: “currency point shall be equivalent to 20,000 shillings”."),
        "tags": ["police", "legal", "currency"],
    },
    # ── The Land (Amendment) Act, 2010 ──────────────────────────────────
    {
        "act": "The Land (Amendment) Act, 2010",
        "section": "Section 1",
        "title": "Determination of annual nominal ground rent by Minister",
        "text": (
            "(3d) Where the board has not determined the annual nominal ground rent "
            "payable by a tenant... within six months after the commencement of the "
            "Land (Amendment) Act 2010, the rent may be determined by the Minister."
        ),
        "tags": ["land", "rent", "minister"],
    },
    {
        "act": "The Land (Amendment) Act, 2010",
        "section": "Section 2 (Inserting Section 32A)",
        "title": "Eviction only for non payment of ground rent",
        "text": (
            "(1) A lawful or bona fide occupant shall not be evicted from registered "
            "land except upon an order of eviction issued by a court and only for non "
            "payment of the annual nominal ground rent."
        ),
        "tags": ["land", "eviction", "occupant"],
    },
    {
        "act": "The Land (Amendment) Act, 2010",
        "section": "Section 2 (Inserting Section 32A, sub 3)",
        "title": "Vacant possession period after eviction order",
        "text": (
            "(3) When making an order for eviction, the court shall state in the "
            "order, the date, being not less than six months after the date of the "
            "order, by which the person to be evicted shall vacate the land."
        ),
        "tags": ["land", "eviction", "court"],
    },
    {
        "act": "The Land (Amendment) Act, 2010",
        "section": "Section 3",
        "title": "Unlawful assignment of tenancy by occupancy",
        "text": (
            "(1a) Subject to subsection (7), a tenant by occupancy who purports to "
            "assign the tenancy... without giving the first option of taking the "
            "assignment... to the owner of the land commits an offence."
        ),
        "tags": ["land", "tenancy", "assignment"],
    },
    {
        "act": "The Land (Amendment) Act, 2010",
        "section": "Section 5",
        "title": "Offence for illegal eviction",
        "text": (
            "(e) [A person who] attempts to evict, evicts, or participates in the "
            "eviction of a lawful or bonafide occupant... without an order of "
            "eviction... is liable on conviction to imprisonment not exceeding seven years."
        ),
        "tags": ["land", "eviction", "offence"],
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
