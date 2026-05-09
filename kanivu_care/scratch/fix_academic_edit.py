import os

file_path = r'c:\Users\jagan\Desktop\kaniv\kanivu_care\kanivu_care\templates\users\academic_edit.html'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

old_form = """    <form action="{% url 'users:academic_edit' %}" method="post" id="form">
        {% csrf_token %}


        <div class="form-group">
            <label for="adno">Admission Number</label>
            <input type="text" name="adno" id="adno" value="{{request.user.memberregistration.adno}}" required>
        </div>

        <div class="form-group">
            <label for="department">Department</label>
            <select name="department" id="department" required>
                <option value="">Select Department</option>
                <option value="bba">BBA</option>
                <option value="bca">BCA</option>
                <option value="bsc_cs">BSC CS</option>
                <option value="bcom_tax">BCOM Tax</option>
                <option value="ttm">TTM</option>
                <option value="bcom_ca_and_finance">BCOM CA and Finance</option>
                <option value="bcom_co_operation">BCOM Co-operation</option>
                <option value="ba_literature">BA Literature</option>
                <option value="ba_communicative_english">BA Communicative English</option>
                <option value="ba_journalism">BA Journalism</option>
                <option value="electronics">Electronics</option>
                <option value="bsw">BSW</option>
            </select>
        </div>

        <div class="form-group">
            <label for="start_year">Start Year</label>
            <input type="text" name="start_year" maxlength="4" id="start_year" value="{{request.user.memberregistration.start_year}}" placeholder="e.g., 2022" inputmode="numeric" required>
        </div>

        <div class="form-group">
            <label for="end_year">End Year</label>
            <input type="text" name="end_year" maxlength="4" id="end_year" value="{{request.user.memberregistration.end_year}}" placeholder="e.g., 2025" inputmode="numeric" required>
        </div>

        <button type="submit" class="btn-submit">Update</button>
    </form>"""

new_form = """    <form action="{% url 'users:academic_edit' %}" method="post" id="form">
        {% csrf_token %}

        <div class="form-group">
            <label for="adno">Admission Number</label>
            <input type="text" name="adno" id="adno" 
                value="{% if request.user.userprofile.role == 'member' %}{{request.user.memberregistration.adno}}{% else %}{{request.user.coordinateregistration.adno}}{% endif %}" 
                required>
        </div>

        <div class="form-group">
            <label for="department">Department</label>
            <select name="department" id="department" required>
                <option value="">Select Department</option>
                {% for val, label in form.fields.department.choices %}
                    <option value="{{ val }}">{{ label }}</option>
                {% endfor %}
            </select>
        </div>

        {% if request.user.userprofile.role == 'member' %}
        <div class="form-group">
            <label for="start_year">Start Year</label>
            <input type="text" name="start_year" maxlength="4" id="start_year" value="{{request.user.memberregistration.start_year}}" placeholder="e.g., 2022" inputmode="numeric" required>
        </div>

        <div class="form-group">
            <label for="end_year">End Year</label>
            <input type="text" name="end_year" maxlength="4" id="end_year" value="{{request.user.memberregistration.end_year}}" placeholder="e.g., 2025" inputmode="numeric" required>
        </div>
        {% else %}
        <div class="form-group">
            <label for="batch">Batch</label>
            <input type="text" name="batch" id="batch" value="{{request.user.coordinateregistration.batch}}" placeholder="e.g., 2022-2025" required>
        </div>

        <div class="form-group">
            <label for="current_year">Current Year</label>
            <select name="current_year" id="current_year" required>
                <option value="">Select Year</option>
                {% for val, label in form.fields.current_year.choices %}
                    <option value="{{ val }}">{{ label }}</option>
                {% endfor %}
            </select>
        </div>
        {% endif %}

        <button type="submit" class="btn-submit">Update</button>
    </form>"""

# Using simple replace because the manual strings might have different indentation than the actual file
# I will try to find the form tag and replace everything until the closing form tag.

import re
pattern = re.compile(r'<form.*?</form>', re.DOTALL)
updated_content = pattern.sub(new_form, content)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(updated_content)
