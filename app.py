from flask import Flask, render_template, request, jsonify
import google.generativeai as genai

# Initialize Flask app
app = Flask(__name__)

# Configure the Google Generative AI API key
genai.configure(api_key="")


def extract_skills_categorized(job_description):
    try:
        prompt = (
            f"Based on the job description '{job_description}', extract exactly 6 technical skills and 6 non-technical skills essential for this role. "
            f"List the skills as headings, separated by commas. Do not number the skills or classify them, just provide two lists separated by commas."
            f"Strictly there should be nothing such as '''## Non-''' in the output text "
        )
        response = genai.GenerativeModel("gemini-1.5-flash").generate_content(prompt)
        skills = response.text.strip()

        # Ensure we have both sections of skills
        if "Technical Skills:" in skills and "Non-Technical Skills:" in skills:
            # Split based on sections
            technical_skills = (
                skills.split("Technical Skills:")[1]
                .split("Non-Technical Skills:")[0]
                .strip()
            )
            non_technical_skills = skills.split("Non-Technical Skills:")[1].strip()

            # Clean and format the skills by filtering out empty or irrelevant entries
            technical_skills_list = "".join(
                [
                    f"<li>{skill.strip()}</li>"
                    for skill in technical_skills.split("*")
                    if skill.strip() and not skill.strip().startswith(":")
                ]
            )
            non_technical_skills_list = "".join(
                [
                    f"<li>{skill.strip()}</li>"
                    for skill in non_technical_skills.split("*")
                    if skill.strip() and not skill.strip().startswith(":")
                ]
            )

            # Combine the cleaned-up lists into formatted HTML for rendering
            formatted_skills = (
                f"<h3>Required Technical Skills:</h3><ul>{technical_skills_list}</ul>"
                f"<h3>Required Non-Technical Skills:</h3><ul>{non_technical_skills_list}</ul>"
            )
            return formatted_skills

        # Return the response if it doesn't match the expected structure
        return f"<p>{skills}</p>"

    except Exception as e:
        return f"Error extracting skills: {str(e)}"


# Function to create a concise, 4-line professional profile summary in paragraph form
def create_profile_summary(job_description, skills):
    prompt = (
        f"Write a concise, strictly 4-line professional summary for a candidate applying to a role based on the following job description: {job_description}. "
        f"Highlight the candidate's key technical skills, {skills}, relevant accomplishments, and ability to contribute to the company's objectives. "
        f"The summary should be recruiter-friendly, without the use of personal pronouns, and focused on the candidate’s qualifications and impact."
    )
    response = genai.GenerativeModel("gemini-1.5-flash").generate_content(prompt)

    # Adding HTML for the profile summary and a copy button
    profile_summary = response.text.strip()
    summary_html = f"""
    <div id="profile-summary" style="position: relative;">
        <p>{profile_summary}</p>
        <button class="copy-btn" onclick="copyToClipboard(event, `{profile_summary}`)" 
                style="background: none; border: none; padding: 0; margin: 0; cursor: pointer;">
            <img src="https://img.icons8.com/ios-glyphs/30/000000/copy.png" alt="Copy Icon" style="vertical-align: middle;">
        </button> <!-- Copy Button with Icon -->
    </div>
    """
    return summary_html


# Function to generate project ideas
def generate_project_ideas(job_description):
    try:
        # Modify the prompt to focus on generating only project titles
        prompt = (
            f"Based on the provided job description, generate exactly 5 project ideas that align with the role. "
            f"Provide each project title in a new line without additional details. "
            f"Here is the job description: {job_description}"
        )
        response = genai.GenerativeModel("gemini-1.5-flash").generate_content(prompt)

        # Split the response by new lines to separate each project title
        project_ideas = response.text.strip().split(
            "\n"
        )  # Split into individual project titles

        # Initialize the HTML content
        project_html = "<h2>5 project ideas based on the job description:</h2>"

        # Process the first 5 project ideas
        for i, idea in enumerate(project_ideas[:5]):  # Ensure only 5 projects
            title = idea.strip()

            # Add the project title to the HTML (ensure it displays properly)
            project_html += f"<p><strong>Project {i+1}:</strong> {title}</p>"

        return project_html

    except Exception as e:
        return f"Error generating project ideas: {str(e)}"


# Function to create professional referral templates for LinkedIn and email
def create_referral_template(recruiter_name, role, company_name, job_link):
    # Email template with HTML formatting
    email_template = (
        f"<strong>Subject:</strong> Referral Request for {role} Position at {company_name}<br><br>"
        f"Hi {recruiter_name},<br><br>"
        f"I hope you’re doing well. I’m reaching out to express my interest in the <strong>{role}</strong> role at <strong>{company_name}</strong>. "
        f"With my experience as a Data Scientist, where I focused on customer analytics, machine learning, LLMs, and data-driven insights, "
        f"I believe I can bring valuable skills to this position.<br><br>"
        f"I would love the opportunity to discuss how my background aligns with <strong>{company_name}</strong>'s needs and explore how I could contribute to your team. "
        f"I’ve attached my resume for your review, and I would appreciate any referral or support you could provide.<br><br>"
        f"Here’s the job link for reference: <a href='{job_link}'>{job_link}</a><br>"
        f"Feel free to visit my portfolio website here: <a href='https://digital-resume-aaryan.vercel.app/'>https://digital-resume-aaryan.vercel.app/</a><br><br>"
        f"Thank you for your time and consideration. I look forward to hearing from you soon.<br><br>"
        f"Best regards,<br>Aaryan Anil"
    )

    # LinkedIn template with HTML formatting
    linkedin_template = (
        f"Hi {recruiter_name},<br><br>"
        f"I hope you’re doing well. I’m reaching out to express my interest in the <strong>{role}</strong> role at <strong>{company_name}</strong>. "
        f"With my experience as a Data Scientist, working with machine learning, LLMs, data analytics, and business intelligence, "
        f"I am confident that my skills would align well with the needs at <strong>{company_name}</strong>.<br><br>"
        f"I would greatly appreciate the opportunity to discuss how my background could contribute to the success of your team. "
        f"I’ve attached my resume for your review, and I would be grateful for any referral or recommendation you could provide.<br><br>"
        f"Here’s the job link for reference: <a href='{job_link}'>{job_link}</a><br>"
        f"Feel free to visit my portfolio here: <a href='https://digital-resume-aaryan.vercel.app/'>https://digital-resume-aaryan.vercel.app/</a><br><br>"
        f"Thank you for considering my request. I look forward to hearing from you soon.<br><br>"
        f"Best regards,<br>Aaryan Anil"
    )

    return linkedin_template, email_template


# Define the routes
@app.route("/", methods=["GET", "POST"])
def index():
    skills = profile_summary = project_ideas = linkedin_template = email_template = None
    job_description = recruiter_name = role = company_name = job_link = ""

    if request.method == "POST":
        job_description = request.form.get("job_description")
        option = request.form.get("option")

        if option == "Extract Relevant Skills":
            skills = extract_skills_categorized(job_description)

        elif option == "Profile Summary":
            skills = extract_skills_categorized(job_description)
            profile_summary = create_profile_summary(job_description, skills)

        elif option == "Project Ideas Based On Job Description":
            project_ideas = generate_project_ideas(job_description)

        elif option == "Referral Template For Linkedin And Email":
            recruiter_name = request.form.get("recruiter_name")
            role = request.form.get("role")
            company_name = request.form.get("company_name")
            job_link = request.form.get("job_link")
            linkedin_template, email_template = create_referral_template(
                recruiter_name, role, company_name, job_link
            )

    return render_template(
        "index.html",
        skills=skills,
        profile_summary=profile_summary,
        project_ideas=project_ideas,
        linkedin_template=linkedin_template,
        email_template=email_template,
        job_description=job_description,
        recruiter_name=recruiter_name,
        role=role,
        company_name=company_name,
        job_link=job_link,
    )


@app.route("/get_result", methods=["POST"])
def get_result():
    option = request.form.get("option")
    job_description = request.form.get("job_description")
    result = ""

    if option == "Extract Relevant Skills":
        result = extract_skills_categorized(job_description)
    elif option == "Profile Summary":
        skills = extract_skills_categorized(job_description)
        result = create_profile_summary(job_description, skills)
    elif option == "Project Ideas Based On Job Description":
        result = generate_project_ideas(job_description)
    elif option == "Referral Template For Linkedin And Email":
        recruiter_name = request.form.get("recruiter_name")
        role = request.form.get("role")
        company_name = request.form.get("company_name")
        job_link = request.form.get("job_link")
        linkedin_template, email_template = create_referral_template(
            recruiter_name, role, company_name, job_link
        )
        result = f"<strong>LinkedIn Template:</strong><br>{linkedin_template}<br><br><strong>Email Template:</strong><br>{email_template}"

    return jsonify({"result": result})


if __name__ == "__main__":
    app.run(debug=True)
