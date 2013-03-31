c2gXMLParse.gridQuestionPossible = function () {
    var assessment_type = $('#assessment_type').val(); 
    return assessment_type == 'survey'; 
}

c2gXMLParse.addGridQuestion = function (html) {
    var editID = $( "#grid-question-edit" )[0].value; 
    var editor_value = editor.getValue(); 
    var editHtml = $(html); 
      
      //Text of question
    var providedText = $('#grid-question-question-text').val(); 
    var questionText = $(editHtml.find('div.question_text')[0]); 
    var questionTextParagraph = $(document.createElement('p')); 
    questionTextParagraph.text(providedText); 
    questionText.empty(); 
    questionText.append(questionTextParagraph); 
      
    var table = $(editHtml.find('table')[0])[0]; 
    
    //create table headings
    var thead = $(document.createElement('thead')); 
    var theadTR = $(document.createElement('tr')); 
    var blankTH = $(document.createElement('th')); 
    theadTR.append(blankTH); 
    var numberOfColumns = 0; 
    for(var i = 1; i < 5; i++)
    {
        var thText = $('#grid-question-column' + i).val(); 
        if(thText)
        {
            var newTH = $(document.createElement('th')); 
            newTH.text(thText); 
            theadTR.append(newTH); 
            numberOfColumns += 1; 
        }
    }
    thead.append(theadTR); 
    $(table).append(thead);
    
    //create questions in table
    var tbody = $(document.createElement('tbody')); 
    for(var i = 1; i < 7; i++)
    {
        var subQuestionText = $('#grid-question-subquestion' + i).val(); 
        if(subQuestionText)
        {
            var tr = $(document.createElement('tr')); 
            var questionTD = $(document.createElement('td')); 
            questionTD.text(subQuestionText); 
            tr.append(questionTD); 
            //add the other columns
            for(var x = 0; x < numberOfColumns; x++)
            {
                var choiceTD = $(document.createElement('td')); 
                var choiceLabel = $(document.createElement('label')); 
                var choiceInput = document.createElement('input'); 
                choiceInput.setAttribute('value', x); 
                choiceInput.setAttribute('type', 'radio'); 
                choiceLabel.append(choiceInput); 
                choiceTD.append(choiceLabel); 
                tr.append(choiceTD); 
            }
            tbody.append(tr); 
        }
    }
    $(table).append(tbody);
    
    //Add to the HTML
    editor_value = editor_value + editHtml[0].outerHTML;                   
    
    mDOM = $(editor_value); 
    editor_value = c2gXMLParse.assignCorrectIds(mDOM, false); 
    editor.setValue(style_html(editor_value, {'max_char':80}));
    editor.onChangeMode();
    
    this.renderPreview(); 
    return true;
}