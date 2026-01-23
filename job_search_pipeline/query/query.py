#                                  MIT License
#                       Copyright 2026, Sébastien Kéroack
# ==============================================================================

from dataclasses import dataclass
from jobspy import scrape_jobs

from job_search_pipeline.utils.format import job_title, salary, company_name
from job_search_pipeline.utils.format.value import na, optional_float, repr_dataclass_short


@dataclass
class Job:
    query: str = ""
    id: str = ""
    site: str = ""
    job_url: str = ""
    job_url_direct: str = ""
    title: str = ""
    company: str = ""
    location: str = ""
    date_posted: str = ""
    job_type: str = ""
    salary_source: str = ""
    interval: str = ""
    min_amount: float = None
    max_amount: float = None
    currency: str = ""
    is_remote: bool = False
    job_level: str = ""
    job_function: str = ""
    listing_type: str = ""
    emails: str = ""
    description: str = ""
    company_industry: str = ""
    company_url: str = ""
    company_logo: str = ""
    company_url_direct: str = ""
    company_addresses: str = ""
    company_num_employees: str = ""
    company_revenue: str = ""
    company_description: str = ""
    skills: str = ""
    experience_range: str = ""
    company_rating: str = ""
    company_reviews_count: str = ""
    vacancy_count: str = ""
    work_from_home_type: str = ""

    @classmethod
    def from_dict(cls, **kwargs) -> "Job":
        return cls(
            query=str(kwargs.get("query", cls.query)),
            id=na(str(kwargs.get("id", cls.id))),
            site=na(str(kwargs.get("site", cls.site))),
            job_url=na(str(kwargs.get("job_url", cls.job_url))),
            job_url_direct=na(str(kwargs.get("job_url_direct", cls.job_url_direct))),
            title=na(str(kwargs.get("title", cls.title))),
            company=na(str(kwargs.get("company", cls.company))),
            location=na(str(kwargs.get("location", cls.location))),
            date_posted=na(str(kwargs.get("date_posted", cls.date_posted))),
            job_type=na(str(kwargs.get("job_type", cls.job_type))),
            salary_source=na(str(kwargs.get("salary_source", cls.salary_source))),
            interval=na(str(kwargs.get("interval", cls.interval))),
            min_amount=optional_float(kwargs.get("min_amount")) or cls.min_amount,
            max_amount=optional_float(kwargs.get("max_amount")) or cls.max_amount,
            currency=na(str(kwargs.get("currency", cls.currency))),
            is_remote=bool(kwargs.get("is_remote", cls.is_remote)),
            job_level=na(str(kwargs.get("job_level", cls.job_level))),
            job_function=na(str(kwargs.get("job_function", cls.job_function))),
            listing_type=na(str(kwargs.get("listing_type", cls.listing_type))),
            emails=na(str(kwargs.get("emails", cls.emails))),
            description=na(str(kwargs.get("description", cls.description))),
            company_industry=na(str(kwargs.get("company_industry", cls.company_industry))),
            company_url=na(str(kwargs.get("company_url", cls.company_url))),
            company_logo=na(str(kwargs.get("company_logo", cls.company_logo))),
            company_url_direct=na(str(kwargs.get("company_url_direct", cls.company_url_direct))),
            company_addresses=na(str(kwargs.get("company_addresses", cls.company_addresses))),
            company_num_employees=na(str(kwargs.get("company_num_employees", cls.company_num_employees))),
            company_revenue=na(str(kwargs.get("company_revenue", cls.company_revenue))),
            company_description=na(str(kwargs.get("company_description", cls.company_description))),
            skills=na(str(kwargs.get("skills", cls.skills))),
            experience_range=na(str(kwargs.get("experience_range", cls.experience_range))),
            company_rating=na(str(kwargs.get("company_rating", cls.company_rating))),
            company_reviews_count=na(str(kwargs.get("company_reviews_count", cls.company_reviews_count))),
            vacancy_count=na(str(kwargs.get("vacancy_count", cls.vacancy_count))),
            work_from_home_type=na(str(kwargs.get("work_from_home_type", cls.work_from_home_type))),
        )

    def title_gendered(self, gender="man") -> str:
        return job_title.transform(self.title, gender=gender) or "N/A"

    def city(self) -> str:
        """Returns city part from location."""
        return self.location.split(",")[0].strip().title() or "N/A"

    def salary(self) -> str:
        return salary.transform(
            min_amount=self.min_amount,
            max_amount=self.max_amount,
            currency=self.currency,
            interval=self.interval,
        )

    def parse(self) -> dict:
        return {
            "date_posted": self.date_posted,
            "source": "python-jobspy",
            "site": self.site,
            "emails": self.emails,
            "company": company_name.transform(self.company),
            "company_description": self.company_description,
            "company_url": self.company_url,
            "title": self.title_gendered(),
            "description": self.description,
            "salary": self.salary(),
            "url": self.job_url,
            "type": self.job_type,
            "city": self.city(),
            "is_remote": str(self.is_remote).upper(),
            "job": repr(self),
        }

    def __repr__(self) -> str:
        return repr_dataclass_short(self)


@dataclass
class Query:
    query: str = ""
    location: str = ""
    distance_unit: int = 50
    distance_use_km: bool = False
    days_old: int = 7
    results_wanted: int = 15
    sort_by: str = "relevance"

    def site_name(self) -> str:
        """Returns site_name part from query."""
        return self.query.split(":", 1)[0].strip().lower()

    def search_term(self) -> str:
        """Returns search_term part from query."""
        return self.query.split(":", 1)[1].strip().lower()

    def country(self) -> str:
        """Returns country part from location."""
        return self.location.split(",")[-1].strip()

    def distance(self) -> int:
        """Returns distance in miles."""
        return int(self.distance_unit // 1.609344) if self.distance_use_km else self.distance_unit

    def hours_old(self) -> int:
        """Converts days_old to hours_old."""
        return self.days_old * 24

    @classmethod
    def from_dict(cls, **kwargs) -> "Query":
        return cls(
            query=str(kwargs.get("query", cls.query)),
            location=str(kwargs.get("location", cls.location)).strip().lower(),
            distance_unit=int(kwargs.get("distance_unit", cls.distance_unit)),
            distance_use_km=bool(kwargs.get("distance_use_km", cls.distance_use_km)),
            days_old=int(kwargs.get("days_old", cls.days_old)),
            results_wanted=int(kwargs.get("results_wanted", cls.results_wanted)),
            sort_by=str(kwargs.get("sort_by", cls.sort_by)).strip().lower(),
        )

    def scrape(self) -> list[dict]:
        return scrape_jobs(
            site_name=self.site_name(),
            search_term=self.search_term(),
            location=self.location,
            country_indeed=self.country(),
            results_wanted=self.results_wanted,
            hours_old=self.hours_old(),
            distance=self.distance(),
            sort_by=self.sort_by,
        ).to_dict(orient="records")

    def run(self) -> list[Job]:
        return [Job.from_dict(query=repr(self), **job) for job in self.scrape()]

    def __repr__(self) -> str:
        return repr_dataclass_short(self)
