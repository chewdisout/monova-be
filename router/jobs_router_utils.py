from models.job import Job
from models.job_translations import JobTranslation

SUPPORTED_LANGS = {"en", "lv", "lt", "pl", "ru", "ee"}

def resolve_lang(lang: str | None) -> str:
    if not lang:
        return "en"
    lang = lang.lower()
    return lang if lang in SUPPORTED_LANGS else "en"

TRANSLATABLE_FIELDS = [
    "title",
    "short_description",
    "full_description",
    "responsibilities",
    "requirements_text",
    "benefits_text",
    "housing_details",
    "documents_required",
    "bonuses",
    "language_required",
]

def job_to_dict(job: Job, lang: str | None = None) -> dict:
    lang = resolve_lang(lang)

    # find matching translation
    tr = next(
        (t for t in (job.translations or []) if t.lang_code == lang),
        None
    )

    def pick(field: str):
        if tr:
            val = getattr(tr, field, None)
            if val:  # use translation only if non-empty
                return val
        return getattr(job, field)

    data = {
        "id": job.id,
        "reference_code": job.reference_code,
        "company_name": job.company_name,
        "country": job.country,
        "city": job.city,
        "workplace_address": job.workplace_address,
        "category": job.category,
        "employment_type": job.employment_type,
        "shift_type": job.shift_type,
        "salary_from": job.salary_from,
        "salary_to": job.salary_to,
        "currency": job.currency,
        "salary_type": job.salary_type,
        "is_net": job.is_net,
        "housing_provided": job.housing_provided,
        "transport_provided": job.transport_provided,
        "min_experience_years": job.min_experience_years,
        "is_active": job.is_active,
        "created_at": job.created_at,
        "updated_at": job.updated_at,
        "image": job.image
    }

    # overlay translatable fields
    for f in TRANSLATABLE_FIELDS:
        data[f] = pick(f)

    return data
