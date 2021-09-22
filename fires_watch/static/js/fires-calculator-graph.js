function generateFiresGraph(data) {
  //https://www.amcharts.com/demos/stacked-column-chart/
  am4core.ready(function () {
    // Themes begin
    am4core.useTheme(am4themes_animated);
    // Themes end

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
    // valueAxis.renderer.inside = true;
    // valueAxis.renderer.labels.template.disabled = true;
    valueAxis.min = 0;

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
      series.columns.template.tooltipText =
        "[bold]{name}[/]\n[font-size:14px]Year {categoryX}\n[bold]€ {valueY}[/]";

      // Add label
      var labelBullet = series.bullets.push(new am4charts.LabelBullet());
      labelBullet.label.text = "{valueY}";
      labelBullet.locationY = 0.5;
      labelBullet.label.hideOversized = true;

      return series;
    }

    portfolio_series = createSeries("portfolio", "Portfolio");
    interest_series = createSeries("interest", "Interest");
    change_series = createSeries("change", "Change");

    // Legend
    chart.legend = new am4charts.Legend();

    // Add scrollbar
    var scrollbar = new am4charts.XYChartScrollbar();
    scrollbar.series.push(portfolio_series);

    chart.scrollbarX = scrollbar;

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

    // Zoom to first 30 years
    chart.events.on("ready", function () {
      categoryAxis.zoomToIndexes(0, 30, false, true);
    });
  }); // end am4core.ready()
}
