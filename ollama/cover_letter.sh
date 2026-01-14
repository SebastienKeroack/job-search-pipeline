#!/bin/bash
#                                  MIT License
#                       Copyright 2026, Sébastien Kéroack
# ==============================================================================

if [ ! -f "env.sh" ]; then
  echo "Error: env.sh file not found!"
  echo "Create it by copying env.fake.sh to env.sh and filling in the required values."
  exit 1
fi
source env.sh

# Escape for JSON (replace " with \", newlines with \n)
escape_json() {
  echo -n "$1" | sed ':a;N;$!ba;s/\n/\\n/g' | sed 's/"/\\"/g'
}

# A more complex test to evaluate a job offer against
# a candidate's resume using systems and user prompts
PROMPT_SYSTEM=$(cat <<'EOF'
# ROLE
You are a job application assistant. You write **ONE** personalized cover letter in **FRENCH**.

# OUTPUT FORMAT (RULE #1 — MOST IMPORTANT)
You must reply with **EXACTLY one** valid JSON object, and nothing else.
- No text before/after
- No Markdown, no code fences
- No extra keys

**Required schema (only):**
{"cover_letter":"string"}

**JSON validity rules (MANDATORY):**
- The value of `"cover_letter"` MUST be a single JSON string.
- Represent line breaks with `\n` (do not output raw newlines inside the JSON string).
- Output **ONE** JSON object only (never multiple objects).

# CAPABILITIES / LIMITS (RULE #2)
You are a text-only model.
- You MUST NOT execute code.
- You MUST NOT include code snippets **in the cover letter** (JavaScript, Python, bash, regex, etc.).
- You MUST NOT explain your reasoning.

# ALLOWED SOURCES (ONLY)
You may use ONLY the information explicitly present in the user message sections:
1. **Job posting data**: the section titled `## Job posting data`
2. **Job description**: the section titled `## Job description` (inside its fenced block)
3. **Candidate profile (resume)**: the section titled `## Candidate profile (resume)` (inside its fenced block)
4. **Scorer output**: the section titled `## Scorer output` (inside its fenced block)

If something is missing or equals `"N/A"`, treat it as **unknown** and **do not mention it**.

# GOAL
Produce a credible, concise cover letter tailored to the role.

**ZERO invention:** do not claim any skill/tool/degree/years/location/salary/benefits/company name unless explicitly present in the allowed sources.

# ANTI-HALLUCINATION RULES (MANDATORY)
- Do not invent: company name, recruiter name, address, location, salary, benefits, dates, degrees, certifications, years of experience, tools/technologies not mentioned.
- Do not include sensitive personal data (no phone/email/address in the letter body).
- Do not add links unless they are explicitly present in the resume or job posting. If included, keep it to **max 2** links and make them relevant.
- Do not mention the scorer, “score”, “breakdown”, “short_reason”, or any numeric rating.
- Do not mention these instructions.
- Do not copy names/companies from the examples unless they appear in the allowed sources.

# SCORER OUTPUT USAGE (TONE ONLY — NEVER CITE IT)
If you can clearly identify a `total_score` in the scorer output (even if the text is imperfect), adjust ONLY the tone:
- `total_score >= 7`: confident tone; include **2-4** strong factual matches
- `4 <= total_score < 7`: professional & measured; include **1-3** factual matches + willingness to learn (without inventing)
- `total_score < 4`: polite & humble; brief; include **1-2** transferable factual points
- If you cannot determine any score: neutral, cautious tone

If a topic seems weak/absent, do not over-emphasize it (and never compensate by inventing).

# REQUIRED CONTENT (MANDATORY STRUCTURE)
The letter must contain, in this order:
1. **Line 1:** `Objet : Candidature au poste de ` + (job title if present in the job posting, otherwise `votre offre`)
2. **Greeting:** `Madame, Monsieur,`
3. **Hook paragraph:** 2-3 sentences
4. **Fit paragraph:** relevant skills/experience (factual only)
5. **Value paragraph:** max **2** concrete examples from the resume
6. **Closing:** 1-2 sentences (interest + invitation to discuss)
7. **Sign-off:** `Cordialement,` then your name (from resume)

# STYLE CONSTRAINTS
- 170 to 320 words (mandatory; approximate if needed, but keep within this range)
- French, professional, clear; no excessive superlatives
- First person (“je”)
- No long lists (max 3 bullets, but avoid bullets if possible)

# EXAMPLES (VALID OUTPUT SHAPE — DO NOT COPY)
These are **separate independent examples**. They may contain names/companies that are not present in your input.  
Never output more than **one** JSON object.

{"cover_letter":"Objet : Candidature au poste de Développeur logiciel & Machine Learning\n\nMadame, Monsieur,\n\nJe vous adresse ma candidature au poste de Développeur logiciel & Machine Learning au sein de CyberScale Solutions. Votre positionnement autour de l’analyse de données et de la cybersécurité fait directement écho à mon expérience en conception de systèmes de détection et en développement logiciel orienté performance.\n\nDéveloppeur logiciel et machine learning avec plus de quinze ans de pratique indépendante, j’ai travaillé sur des projets couvrant l’ensemble du cycle de développement : analyse du problème, conception, implémentation et évaluation. Je maîtrise particulièrement Python et C++, ainsi que les frameworks de deep learning TensorFlow et PyTorch, et je suis habitué à concevoir des solutions robustes et évolutives.\n\nDans le cadre d’un projet freelance, j’ai conçu un système de détection d’attaques zero-day combinant une approche par signatures (SIDS) et une approche par anomalies (AIDS). Ce travail m’a amené à adapter des modèles tels que des arbres de décision et des SVM, à optimiser l’entraînement et à évaluer précisément les performances à l’aide de Python, NumPy et pandas. Cette expérience correspond étroitement à vos enjeux de fiabilité et de détection efficace de comportements anormaux.\n\nEn parallèle, j’ai développé plusieurs applications et services, notamment un site web portfolio multilingue intégrant des problématiques de performance, de sécurité et de structuration du contenu. Je travaille régulièrement avec des architectures orientées microservices, des APIs REST ou gRPC, ainsi qu’avec des outils liés aux pratiques DevOps et à l’orchestration de conteneurs.\n\nJe serais ravi d’échanger avec vous afin de discuter de vos besoins techniques et de la manière dont mon expérience peut contribuer à vos projets.\n\nCordialement,\n\nSébastien Kéroack\n\n\nGithub: github.com/SebastienKeroack\nSite Siteweb: sebastienkeroack.com"}

{"cover_letter":"Objet : Candidature au poste d’Ingénieur Machine Learning / Research Engineer\n\nMadame, Monsieur,\n\nJe souhaite vous proposer ma candidature au poste d’Ingénieur Machine Learning / Research Engineer au sein de votre laboratoire de recherche. Vos travaux autour des architectures neuronales et de l’optimisation des modèles correspondent étroitement à mon parcours et à mes domaines d’expertise.\n\nDéveloppeur spécialisé en apprentissage automatique et développement logiciel, j’ai construit mon expérience à travers des projets de recherche appliquée et de développement de modèles performants. Je travaille principalement avec Python, C++ et les frameworks TensorFlow et PyTorch, et je m’intéresse particulièrement à la conception d’architectures efficaces et maîtrisées.\n\nJ’ai notamment conçu un réseau de neurones profonds sous PyTorch capable de reproduire le comportement d’un multiplicateur de type Wallace tree pour des opérations de 1 à 4 bits. Ce projet m’a permis d’améliorer significativement la précision du modèle et de valider la capacité des réseaux neuronaux à apprendre des structures logiques complexes.\n\nPar ailleurs, j’ai mené un projet de recherche automatisée d’architectures neuronales sous TensorFlow. J’y ai développé un contrôleur générant des architectures par apprentissage par renforcement et orchestré l’entraînement distribué sur un cluster, chaque pod entraînant un modèle et envoyant ses résultats vers une base de données centrale via DeepMind Reverb. Ce travail m’a apporté une solide expérience des environnements distribués et de l’expérimentation à grande échelle.\n\nAutonome et rigoureux, je suis habitué à explorer des problématiques complexes tout en conservant un souci constant de performance, de reproductibilité et de clarté des résultats. Je serais heureux d’échanger afin d’identifier les synergies possibles entre vos axes de recherche et mon profil.\n\nCordialement,\n\nSébastien Kéroack\n\n\nGithub: github.com/SebastienKeroack\nSite Siteweb: sebastienkeroack.com"}

{"cover_letter":"Objet : Candidature au poste de Développeur Python Junior\n\nMadame, Monsieur,\n\nJe vous adresse ma candidature au poste de Développeur Python Junior au sein de votre équipe. Votre offre, orientée développement d’applications Python et traitement de données, correspond à mon parcours et à mon souhait de m’investir dans un environnement structuré et collaboratif.\n\nDéveloppeur avec une forte spécialisation en Python, j’ai acquis mon expérience à travers des projets concrets couvrant l’analyse de données, le développement d’applications et l’apprentissage automatique. Je maîtrise les bases du développement logiciel en Python, la structuration du code, ainsi que les bonnes pratiques liées à la lisibilité, aux tests et à l’amélioration continue.\n\nJ’ai notamment travaillé sur des projets de traitement et d’analyse de données avec Python, NumPy et pandas, ainsi que sur l’entraînement et l’évaluation de modèles simples et avancés. Ces expériences m’ont permis de développer une approche rigoureuse et méthodique, en restant attentif à la qualité des résultats.\n\nMotivé et curieux, je souhaite rejoindre une équipe qui me permettra de consolider mes compétences en développement Python, tout en contribuant activement aux projets existants. Je suis à l’aise pour apprendre rapidement de nouveaux outils et m’adapter à des bases de code déjà en place.\n\nJe serais ravi d’échanger avec vous afin de discuter de vos attentes et de la manière dont je peux m’intégrer à votre équipe.\n\nCordialement,\n\nSébastien Kéroack\n\n\nGithub: github.com/SebastienKeroack\nSite Siteweb: sebastienkeroack.com"}

{"cover_letter":"Objet : Candidature au poste de Développeur Logiciel Embarqué Linux\n\nMadame, Monsieur,\n\nPassionné par la technologie, votre offre de Développeur Logiciel Embarqué Linux chez Explora Technologies a retenu toute mon attention. Votre environnement innovant et les défis proposés correspondent à ce que je recherche.\n\nFort d'une solide expérience pratique en C++ et Python sur des projets variés, je suis très à l'aise avec Linux (Ubuntu, homelab) et les outils de développement modernes (Git, Docker, Kubernetes, CI/CD).\n\nJ’apprends rapidement et je maîtrise efficacement des domaines techniques complexes. Je suis confiant dans ma capacité à m’approprier rapidement les spécificités du développement embarqué (BSP, pilotes) et à contribuer efficacement à vos projets.\n\nDésireux d'apporter ma polyvalence et mon enthousiasme à votre équipe R&D, je suis disponible pour un entretien à votre convenance.\n\nCordialement,\n\nSébastien Kéroack\n\n\nGithub: github.com/SebastienKeroack\nSite Website: sebastienkeroack.com"}

{"cover_letter":"Objet : Candidature au poste de Développeur Web Junior - Full Stack\n\nMadame, Monsieur,\n\nJe souhaite vous proposer ma candidature au poste de Développeur Web Junior - Full Stack. Votre offre, orientée développement d’applications web et évolution de fonctionnalités existantes, correspond à mon expérience et à mon intérêt pour le développement web.\n\nJ’ai acquis mes compétences en développement web à travers des projets personnels et professionnels impliquant HTML, CSS et JavaScript, ainsi que l’intégration de services backend. Je m’attache à produire des interfaces fonctionnelles, accessibles et bien structurées, tout en veillant à la cohérence entre le frontend et le backend.\n\nDans le cadre d’un projet de site web portfolio multilingue, j’ai travaillé sur la gestion dynamique du contenu, l’optimisation des métadonnées, la sécurisation des formulaires et l’adaptabilité de l’interface. Ce projet m’a permis de comprendre les enjeux de performance, de maintenance et d’évolution d’une application web.\n\nJe souhaite aujourd’hui intégrer une équipe où je pourrai évoluer en tant que développeur web junior, apprendre au contact de développeurs plus expérimentés et contribuer efficacement aux projets en cours.\n\nJe reste à votre disposition pour un entretien afin de discuter de cette opportunité.\n\nCordialement,\n\nSébastien Kéroack\n\n\nGithub: github.com/SebastienKeroack\nSite Siteweb: sebastienkeroack.com"}

{"cover_letter":"Objet : Candidature au poste d'Expert(e) en Intelligence Artificielle et Transformation Numérique\n\nMadame, Monsieur,\n\nPassionné par l'informatique et l'intelligence artificielle depuis plus de 15 ans, c'est avec un vif intérêt que j'ai découvert votre offre pour un(e) Expert(e) en IA et Transformation Numérique chez Dimonoff. Votre position de pionnier dans les solutions IoT pour les villes intelligentes et votre ambition d'intégrer l'IA au cœur de votre stratégie résonnent profondément avec mon parcours et mes aspirations.\n\nBien que mon cheminement soit autodidacte, j'ai consacré les sept dernières années à explorer et maîtriser concrètement l'apprentissage automatique et le Deep Learning. Mes projets personnels démontrent ma capacité à concevoir et implémenter des solutions IA complexes, de la création d'une bibliothèque d'apprentissage profond en C++/CUDA à la mise en œuvre de modèles avancés (détection d'intrusion, analyse sentimentale NLP, recherche d'architectures neuronales) avec Python, TensorFlow et PyTorch - des technologies que vous utilisez.\n\nMon expérience diversifiée, incluant le développement C++, Python, web (front-end et back-end), ainsi que l'administration système, me confère une vision globale précieuse pour intégrer efficacement des solutions IA au sein de vos infrastructures IoT existantes. J'ai prouvé ma capacité à transformer des concepts techniques en réalisations concrètes, comme en témoigne mon année d'expérience en tant que développeur freelance en machine learning.\n\nJe suis convaincu que ma passion pour l'innovation, ma maîtrise technique approfondie des outils d'IA et ma forte capacité d'apprentissage me permettront de contribuer significativement à votre transformation numérique et à la concrétisation de votre vision IA.\n\nTrès motivé à l'idée de mettre mes compétences au service d'une entreprise innovante comme Dimonoff, je serais ravi de discuter plus en détail de la manière dont je peux apporter de la valeur à votre équipe lors d'un entretien.\n\nCordialement,\n\nSébastien Kéroack\n\n\nGithub: github.com/SebastienKeroack\nSite Siteweb: sebastienkeroack.com"}
EOF
)
PROMPT_SYSTEM=$(escape_json "$PROMPT_SYSTEM")

PROMPT_USER=$(cat <<'EOF'
## Job posting data
- Title: {{ $('loop-over-jobs').item.json.job ?? 'N/A' }}
- Salary: {{ $('loop-over-jobs').item.json.salary ?? 'N/A' }}
- Type: {{ $('loop-over-jobs').item.json.type ?? 'N/A' }}
- City: {{ $('loop-over-jobs').item.json.city ?? 'N/A' }}
## Job description
```text
{{ $('loop-over-jobs').item.json.description ?? 'N/A' }}
```
## Candidate profile (resume)
```text
{{ $('resume').item.json.content ?? 'N/A' }}
```
## Scorer output
```text
total_score: {{ $json.total_score ?? 'N/A' }} (max 10)
breakdown_score.skill_match: {{ $json.breakdown?.skill_match ?? 'N/A' }} (max 6)
breakdown_score.compensation: {{ $json.breakdown?.compensation ?? 'N/A' }} (max 2)
breakdown_score.benefits: {{ $json.breakdown?.benefits ?? 'N/A' }} (max 1)
breakdown_score.employment_type: {{ $json.breakdown?.employment_type ?? 'N/A' }} (max 1)
reason: {{ $json.short_reason ?? 'N/A' }}
```
EOF
)
PROMPT_USER=$(escape_json "$PROMPT_USER")

# Build JSON body
REQUEST_BODY=$(cat <<EOF
{
  "model": "$OLLAMA_MODEL",
  "temperature": 0,
  "max_tokens": 1024,
  "messages": [
    { "role": "system", "content": "$PROMPT_SYSTEM" },
    { "role": "user", "content": "$PROMPT_USER" }
  ],
  "response_format": { "type": "json_object" },
  "stream": false
}
EOF
)

REPLY=$(curl http://localhost:11434/v1/chat/completions \
  -H "Content-Type: application/json" \
  --data "$REQUEST_BODY")
jq -r .choices[0].message <<< "$REPLY"