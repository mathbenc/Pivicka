var currentTheme = "light";
function themeSetter() {
  var today = new Date();
  var h = today.getHours();
  if (h > 20 || h < 7) {
    $("html").css("background-color", "#212121")
    $("body").css("background-color", "#212121")

    $("#logotip").attr("src", "./static/images/icon-test-dark-alt-min.png");
    $("#logotipWebp").attr("srcset", "./static/images/icon-test-dark-alt.webp");
    $("#logotipPng").attr("srcset", "./static/images/icon-test-dark-alt-min.png");

    $("#dataTable").addClass("my-table-dark");
    $(".fakeThead").css("background-color", "#212121");
    
    $("thead th").css("background-color", "#212121")
    $("thead th").css("color", "white")

    $(".modal-content").addClass("elegant-color");
    $(".modal-body").addClass("text-white");

    currentTheme = "dark"
  }
}
themeSetter();

var country = "";
$.ajax({
  url: "https://ipinfo.io?token=0b3053efc15e81",
  type: "get",
  dataType: "jsonp",
  success: function(data) {
    country = data.country;
    colorCountry();
  }
})

var region = "";

// Search
$("#search").on("keyup", function () {
  var value = $(this).val().toLowerCase();
  $("#dataTable tbody tr").filter(function () {
    $(this).toggle($(this).text().toLowerCase().indexOf(value) > -1)
  });
  colorCountry();
});

// Zaženemo plugin za sortiranje
var table = document.getElementById('dataTable');
var sort = new Tablesort((table), { descending: true });

function tableBodyCreate(region) {
  var tbdy = document.getElementById("tableBody");
  $("#dataTable tbody").empty();
  for (var i = 0; i < data.length; i++) {
    if (data[i]["continent"] == region || region == "") {
      var row = tbdy.insertRow();
      var cell = row.insertCell();
      row.setAttribute("class", "countryExpand");
      row.setAttribute("id", i);
      cell.innerHTML = data[i]["translation"]
      cell.setAttribute("id", data[i]["countryInfo"]["iso2"])
      cell = row.insertCell();
      cell.setAttribute("align", "right");
      cell.setAttribute("class", "d-none d-xl-table-cell text-right");
      cell.innerHTML = data[i]["population"];
      cell = row.insertCell();
      cell.setAttribute("align", "right");
      cell.setAttribute("class", "d-none d-sm-table-cell text-right");
      cell.innerHTML = data[i]["cases"];
      cell = row.insertCell();
      cell.setAttribute("align", "right");
      if (data[i]["todayCases"] != "0") {
        cell.style.color = "#FF0266";
      }
      cell.innerHTML = data[i]["todayCases"];
      cell = row.insertCell();
      cell.setAttribute("align", "right");
      cell.setAttribute("class", "d-none d-md-table-cell text-right");
      cell.innerHTML = data[i]["casesPerOneMillion"];
      cell = row.insertCell();
      cell.setAttribute("align", "right");
      cell.setAttribute("class", "d-none d-md-table-cell text-right");
      cell.innerHTML = data[i]["deaths"];
      cell = row.insertCell();
      cell.setAttribute("align", "right");
      if (data[i]["todayDeaths"] != 0) {
        cell.style.color = "#FF0266";
      }
      cell.innerHTML = data[i]["todayDeaths"];
      cell = row.insertCell();
      cell.setAttribute("align", "right");
      cell.setAttribute("class", "d-none d-lg-table-cell text-right");
      cell.innerHTML = data[i]["deathsPerOneMillion"];
      cell = row.insertCell();
      cell.setAttribute("align", "right");
      cell.setAttribute("class", "d-none d-lg-table-cell text-right");
      cell.innerHTML = data[i]["recovered"];
      cell = row.insertCell();
      cell.setAttribute("align", "right");
      cell.setAttribute("class", "d-none d-md-table-cell text-right");
      cell.innerHTML = data[i]["active"];
      /*
      cell = row.insertCell();
      cell.setAttribute("align", "right");
      cell.setAttribute("class", "d-none d-xl-table-cell text-right");
      cell.innerHTML = data[i]["tests"];
      */
      cell = row.insertCell();
      cell.setAttribute("align", "right");
      cell.innerHTML = data[i]["newTests"];
      cell = row.insertCell();
      cell.setAttribute("align", "right");
      cell.setAttribute("class", "d-none d-xl-table-cell text-right");
      cell.innerHTML = data[i]["testsPerOneMillion"];
    }
  }
  sort.refresh();
  $("tbody").show();
  colorCountry();
}

tableBodyCreate(region);

themeSetter();

function colorCountry() {
  var table = $("#dataTable");
  var rows = table.find("tr");
  for (var i = 1; i < rows.length; i++) {
    var cells = rows[i].getElementsByTagName("td")
    if (cells[0].getAttribute("id")==country) {
      rows[i].classList.add("myCountry");
      rows[i].style.backgroundColor = "#ffff72";
      rows[i].style.color = "black";
    }
  }
};

$(document).on(colorCountry(), "#dataTable", function(){});

$(document).ready(function() {
  $(document).on("click", ".countryExpand" , function() {
    var i = $(this).attr("id");
    $("#countryDetailsModalTitle").text(data[i]["translation"]);
    $("#populationModal").text(data[i]["population"]);
    $("#infectedModal").text(data[i]["cases"]);
    $("#infectedTodayModal").text(data[i]["todayCases"]);
    $("#infectedRatioModal").text(data[i]["casesPerOneMillion"]);
    $("#deadModal").text(data[i]["deaths"]);
    $("#deadTodayModal").text(data[i]["todayDeaths"]);
    $("#deadRatioModal").text(data[i]["deathsPerOneMillion"]);
    $("#curedModal").text(data[i]["recovered"]);
    $("#activeModal").text(data[i]["active"]);
    $("#criticalModal").text(data[i]["critical"]);
    $("#countryFlag").attr("src", data[i]["countryInfo"]["flag"])
    $("#testsModal").text(data[i]["tests"]);
    $("#newTestsModal").text(data[i]["newTests"]);
    $("#testsRatioModal").text(data[i]["testsPerOneMillion"]);
    $("#countryDetailsModal").modal("show");
    showGraph(data[i].country);
  })
})

$(".tableFixHead").on("scroll", function (event) {
  var y = $(this).scrollTop(); 
  if (y > 0) {  
    $(".fakeThead").addClass('shadows'); 
  }
  else { 
    $(".fakeThead").removeClass('shadows'); 
  }
});

$(document).ready(function() {
  $("#logotip").click(function() {
    switchTheme();
  })
})

function switchTheme() {
  if (currentTheme == "light") {
    $("#logotip").attr("src", "./static/images/icon-test-dark-alt-min.png");
    $("#logotipWebp").attr("srcset", "./static/images/icon-test-dark-alt.webp");
    $("#logotipPng").attr("srcset", "./static/images/icon-test-dark-alt-min.png");
    $("html").css("background-color", "#212121")
    $("body").css("background-color", "#212121")

    $("#dataTable").addClass("my-table-dark");
    $(".fakeThead").css("background-color", "#212121");
    
    $("thead th").css("background-color", "#212121")
    $("thead th").css("color", "white")

    $(".modal-content").addClass("elegant-color");
    $(".modal-body").addClass("text-white");
    currentTheme = "dark"
  }
  else {
    // vklopimo light theme
    $("#logotip").attr("src", "./static/images/icon-test-alt-min.png");
    $("#logotipWebp").attr("srcset", "./static/images/icon-test-alt.webp");
    $("#logotipPng").attr("srcset", "./static/images/icon-test-alt-min.png");
    $("html").css("background-color", "white")
    $("body").css("background-color", "white")

    $("#dataTable").removeClass("my-table-dark");
    $(".fakeThead").css("background-color", "white");
    
    $("thead th").css("background-color", "white")
    $("thead th").css("color", "black")

    $(".modal-content").removeClass("elegant-color");
    $(".modal-body").removeClass("text-white");
    currentTheme = "light"
  }
}

  var ctxL = document.getElementById("lineChart").getContext('2d');
  var myLineChart = new Chart(ctxL, {
    type: 'line',
    data: {
      labels: Object.keys(graphData[0].timeline.cases),
      datasets: [
        {
          label: "Umrli",
          data: Object.values(graphData[0].timeline.deaths),
          backgroundColor: [
            'rgba(255, 69, 69, .4)',
          ],
          borderColor: [
            'rgba(255, 69, 69, 1)',
          ],
          borderWidth: 2
        },
        {
          label: "Ozdraveli",
          data: Object.values(graphData[0].timeline.recovered),
          backgroundColor: [
            'rgba(0, 177, 106, .4)',
          ],
          borderColor: [
            'rgba(0, 177, 106, 1)',
          ],
          borderWidth: 2
        },
        {
          label: "Okuženi",
          data: Object.values(graphData[0].timeline.cases),
          backgroundColor: [
            'rgba(247, 202, 24, .4)',
          ],
          borderColor: [
            'rgba(247, 202, 24, 1)',
          ],
          borderWidth: 2
        }
      ] 
    },
    options: {
      responsive: true,
      scales: {
        xAxes: [{
          gridLines: {
            color: '#ffeb3b',
            zeroLineColor: "yellow",
            display:false,
          }
        }],
        yAxes: [{
          gridLines: {
            color: '#ffeb3b',
            zeroLineColor: "#ffffff",
            display:false,
          },
          labels: {
            color: 'yellow',
            fontColor: 'red'
          }  
        }]
      },
      legend: {
        position: "bottom"
      },
      elements: {
        point: {
          radius: 0
        }
      }
    }
  });

  /*
  var ctxL = document.getElementById("globalChart").getContext('2d');
  var myGlobalChart = new Chart(ctxL, {
    type: 'line',
    data: {
      labels: graphData["dates"],
      datasets: [
        {
          label: "Umrli",
          data: graphGlobal["global_deaths"],
          backgroundColor: [
            'rgba(255, 69, 69, .4)',
          ],
          borderColor: [
            'rgba(255, 69, 69, .8)',
          ],
          borderWidth: 2
        },
        {
          label: "Okuženi",
          data: graphGlobal["global_confirmed"],
          backgroundColor: [
            'rgba(0, 184, 107, .25)',
          ],
          borderColor: [
            'rgba(0, 184, 107, .5)',
          ],
          borderWidth: 2
        }
      ] 
    },
    options: {
      responsive: true,
      scales: {
        xAxes: [{
          gridLines: {
            color: '#ffeb3b',
            zeroLineColor: "yellow",
            display:false,
          }
        }],
        yAxes: [{
          gridLines: {
            color: '#ffeb3b',
            zeroLineColor: "#ffffff",
            display:false,
          },
          labels: {
            color: 'yellow',
            fontColor: 'red'
          }  
        }]
      },
      legend: {
        position: "bottom"
      },
      elements: {
        point: {
          radius: 0
        }
      }
    }
  });
  */

function showGraph(countryCode) {
    for(var i=0;i<graphData.length;i++) {
      if(graphData[i].country == countryCode) {
        myLineChart.data.labels = Object.keys(graphData[i].timeline.cases);
        myLineChart.data.datasets[0].data = Object.values(graphData[i].timeline.deaths);
        myLineChart.data.datasets[2].data = Object.values(graphData[i].timeline.cases);
        myLineChart.data.datasets[1].data = Object.values(graphData[i].timeline.recovered);
        myLineChart.update();
        break;
      }
    }
}

function modeSwitch() {
  $("#globeSwitch")[0].classList.toggle("fa-globe-europe");
  if (region == "Europe") {
    region = ""
    $("#globeText").text(" Svet\xa0\xa0");
    $("#globalDeaths").text(globalData["deaths"]);
    $("#globalRecovered").text(globalData["recovered"]);
    $("#globalCases").text(globalData["cases"]);
    /*
    myGlobalChart.data.datasets[1].data = graphGlobal["global_confirmed"];
    myGlobalChart.data.datasets[0].data = graphGlobal["global_deaths"];
    myGlobalChart.update();
    */
    $("#regionTitle").text("Svet");
  }
  else {
    region = "Europe";
    for(var i=0;i<europeData.length;i++) {
      if(europeData[i]["continent"] == "Europe") {
        $("#globeText").text(" Evropa");
        $("#globalDeaths").text(europeData[i]["deaths"]);
        $("#globalRecovered").text(europeData[i]["recovered"]);
        $("#globalCases").text(europeData[i]["cases"]);
      }
     }
    /*
    myGlobalChart.data.datasets[1].data = graphGlobal["europe_confirmed"];
    myGlobalChart.data.datasets[0].data = graphGlobal["europe_deaths"];
    myGlobalChart.update();
    */
    $("#regionTitle").text("Evropa");
  };
  tableBodyCreate(region);
  colorCountry();
}

if ('serviceWorker' in navigator) {
  // sw.js can literally be empty, but must exist
  navigator.serviceWorker.register('/sw.js');
}