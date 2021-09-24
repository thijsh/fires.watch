function generateFiresGraph(data) {
  // https://www.amcharts.com/demos/stacked-column-chart/
  am4core.ready(function () {
    // Themes
    am4core.useTheme(am4themes_animated);

    // Create chart instance
    var chart = am4core.create("chartdiv", am4charts.XYChart);

    // Add data
    chart.data = data;

    // Create axes
    var categoryAxis = chart.xAxes.push(new am4charts.CategoryAxis());
    categoryAxis.dataFields.category = "year";
    categoryAxis.title.text = "Years from now ->";
    categoryAxis.showOnInit = false; // Zoom in before showing results
    // categoryAxis.renderer.grid.template.location = 0;

    var valueAxis = chart.yAxes.push(new am4charts.ValueAxis());
    valueAxis.title.text = "Value ->";
    valueAxis.min = 0;

    // valueAxis.renderer.labels.template.disabled = true;
    // valueAxis.renderer.inside = true;

    // Create series
    function createSeries(field, name) {
      // Set up series
      var series = chart.series.push(new am4charts.ColumnSeries());
      series.name = name;
      series.dataFields.valueY = field;
      series.dataFields.categoryX = "year";
      series.sequencedInterpolation = true;

      // Make it stacked
      series.stacked = true;

      // Configure columns
      series.columns.template.width = am4core.percent(60);
      // series.columns.template.tooltipText =
      series.tooltipText =
        "[bold]{name}[/]\n[font-size:14px]Year {categoryX}\n[bold]€ {valueY.formatNumber('###,###.##')}[/]";

      return series;
    }

    portfolio_series = createSeries("portfolio", "Portfolio");
    interest_series = createSeries("interest", "Interest");
    change_series = createSeries("change", "Transactions");

    // Legend
    chart.legend = new am4charts.Legend();
    chart.legend.itemContainers.template.paddingTop = 25;

    // Add scrollbar
    var scrollbar = new am4charts.XYChartScrollbar();
    scrollbar.series.push(portfolio_series);
    chart.scrollbarX = scrollbar;

    // Cursor
    chart.cursor = new am4charts.XYCursor();
    // chart.cursor.lineY.disabled = true;
    valueAxis.cursorTooltipEnabled = false;

    // Disable grid labels
    categoryAxis.renderer.grid.template.disabled = true;
    valueAxis.renderer.grid.template.disabled = true;

    // Guide
    // var range = valueAxis.axisRanges.create();
    // range.value = 1000000;
    // range.axisFill.fill = am4core.color("#396478");
    // range.axisFill.fillOpacity = 0.2;
    // range.grid.strokeOpacity = 0;
    // range.grid.strokeWidth = 2;

    chart.numberFormatter.numberFormat = "#.a"; // Format big numbers
    valueAxis.calculateTotals = true; // Calculate total stacked values

    // Responsive
    chart.responsive.enabled = true;
    chart.responsive.rules.push({
      relevant: function (target) {
        if (target.pixelWidth <= 600) {
          return true;
        }
        return false;
      },
      state: function (target, stateId) {
        return;
      },
    });

    // Zoom in to first 30 years
    chart.events.on("ready", function () {
      categoryAxis.zoomToIndexes(0, 30, false, true);
    });
  }); // end am4core.ready()
}
