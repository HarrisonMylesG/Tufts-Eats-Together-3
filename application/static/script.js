var list_names; //to avoid putting them in the html, which breaks them up from escape chars

$(document).ready(function(){

    /* MENU BUTTON (MOBILE) */
     $(document).on("click", "#menu-dropdown-button", function() //when we click menu
    {
        if (document.getElementsByClassName("menu-items")[0].style.height > "0px")
        {
            $("#menu-items").animate({'height': "0"});
            $("body").animate({'margin-top': "100"});
        }
        else
        {
            $("#menu-items").animate({'height': "50"});
            $("body").animate({'margin-top': "150"});
        }
    });
    $(document).click(function(e) //click out of menu
    {
        if (!e.target.className.includes("menu-dropdown-button") && document.getElementsByClassName("menu-items")[0].style.height == "50px")
        {
            $("#menu-items").animate({'height': "-=50"});
            $("body").animate({'margin-top': "-=50"});
        }
    });


    $(document).on("click", ".big-button", function(e) //when we click the trip button
    {
        var location = e.target.dataset.location;
        var time_start = getSelectedValue("timeSelect");
        var duration_minutes = getSelectedValue("durSelect");
        console.log(time_start, duration_minutes);
        var time_end = calculateTime(time_start, duration_minutes);
        var location_selection = {location, time_start, time_end};
        // console.log(location);

        function getSelectedValue(element_id) {
            const select = document.getElementById(element_id);
            const selectedOption = select.options[select.selectedIndex];

            if (selectedOption) {
                let selectedValue = selectedOption.value;
                if (selectedValue == "now") {
                    const currentTimeStr = getCurrentTimeAsString();
                    // console.log(currentTimeStr); // Example output: "18:45"
                    selectedValue = currentTimeStr;
                }
                console.log("Selected value:", selectedValue);
                return selectedValue;
                // You can replace the console.log with any other action you want to perform with the selected value.
            } else {
                console.log("No option selected");
            }
        }

        function getCurrentTimeAsString() {
            const now = new Date();
            const hours = now.getHours().toString().padStart(2, "0");
            const minutes = now.getMinutes().toString().padStart(2, "0");

            const timeStr = `${hours}:${minutes}`;

            return timeStr;
        }

        function calculateTime(selectedValue, minutesToAdd) {
            console.log("calc TIME:", selectedValue, minutesToAdd);
            // Parse the selected time value (HH:MM) into hours and minutes
            const [hours, minutes] = selectedValue.split(":").map(Number);

            // Calculate the total minutes
            const totalMinutes = hours * 60 + minutes + Number(minutesToAdd);
            console.log("found hoursmin:", hours, minutes);
            console.log("comp total min:", totalMinutes);

            // Calculate the new hours and minutes
            const newHours = Math.floor(totalMinutes / 60) % 24;
            const newMinutes = totalMinutes % 60;
            console.log("new vals", newHours, newMinutes);

            // Format the result as HH:MM (24-hour format)
            const result = `${String(newHours).padStart(2, "0")}:${String(newMinutes).padStart(2, "0")}`;
            console.log("time ending computed: ", result);

            return result;
        }

        ajax("/home", JSON.stringify({location_selection}), fillTable);
        function fillTable(data)
        {
            $("#list-data").html(data);
        }

    });


    // ALERT POPUP
    function showAlert(text)
    {
        $(".search-box").removeClass("top");
        $("#listDropdown").slideUp(750, function(){setTimeout(function(){$(".listDropdown").empty();},250);});
        var stuff = "<div class='form'><div class='alert-desc'>" + text + "</div>"
        stuff += "<button class='form-button' id='okay-button'>OKAY</button></div>"
        $("#alert-stuff").html(stuff);
        $("#alert").css("display", "block");
    }
    $(document).on("click", "#okay-button", function() //when we click the alert okay button
    {
        $("#alert").css("display", "none");
    });
    $(document).on("click", ".alert-close", function() //when we click the alert x button
    {
        $("#alert").css("display", "none");
    });
    $(document).on("click", "#deactivate-account", function() //when we click the deactivate account button
    {
        var stuff = "<div class='form'><div class='alert-desc'>are you sure you want to PERMANENTLY delete ALL data associated with this account?</div>"
        stuff += "<button class='form-button' id='kill-button'>DEACTIVATE</button></div>"
        $("#alert").css("display", "block");
        $("#alert-stuff").html(stuff);
        $("#kill-button").click(function(e) //when we click the dropdown button
        {
            e.stopPropagation();
            var deactivate_account = "KILL HIM!";
            ajax("/account", JSON.stringify({deactivate_account}));
            window.location = "/logout";
        });
    });






    //LOGIN SCREEN ON SPACEBAR
    $(document).keypress(function(event) //if a key is pressed
    {
        var keycode = (event.keyCode ? event.keyCode : event.which);
        var loggedOut = String($(".message-light").html())
        //console.log(loggedOut.length);
        if (loggedOut.length > 10) //if we are logged out on home screen, bring us to login page on spacebar
        {
            //console.log(loggedOut);
            if (keycode = '32')
            {
                document.location.href = "/login";
            }
        }
    });

    function ajax(url_, data_, function_)
    {
        var params =
        {
            url: url_,
            type: "POST",
            contentType: "application/json",
            data: data_,
        };
        //console.log(params);
        $.ajax(params).done
        (
            function(data)
            {
                if (function_)
                {
                    function_(data);
                }
            }
        );
    }

    function debounce(fn, delay)
    {
        var timer = null;
        return function()
        {
          var context = this, args = arguments;
          clearTimeout(timer);
          timer = setTimeout(function()
          {
            fn.apply(context, args);
          }, delay);
        };
    }

});