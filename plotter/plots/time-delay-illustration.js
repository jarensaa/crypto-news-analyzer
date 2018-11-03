d3.json("/data/time-delay-data.json", function(error, data) {
  function generatePlotGroup(xScale, yScale, dataset) {
    var linePlot = new Plottable.Plots.Line()
      .addDataset(new Plottable.Dataset(dataset))
      .x(function(d) {
        return d.time;
      }, xScale)
      .y(function(d) {
        return d.value;
      }, yScale)
      .attr("opacity", 0.9);

    return linePlot;
  }

  var xScale = new Plottable.Scales.Linear().domain([0, 50]);
  var xLabel = new Plottable.Components.AxisLabel("Time", 0);

  var marketDataYScale = new Plottable.Scales.Linear();
  var postDataYScale = new Plottable.Scales.Linear();
  var socialMediaDataYScale = new Plottable.Scales.Linear().domain([75, 140]);

  var marketDataPlot = generatePlotGroup(
    xScale,
    marketDataYScale,
    data.marketData
  );

  var postDataPlot = generatePlotGroup(xScale, postDataYScale, data.postData);

  var socialMediaDataPlot = generatePlotGroup(
    xScale,
    socialMediaDataYScale,
    data.redditData
  );

  var marketDataXAxis = new Plottable.Axes.Numeric(xScale, "bottom");
  var marketDataYAxis = new Plottable.Axes.Numeric(marketDataYScale, "left");
  var marketDataLabel = new Plottable.Components.AxisLabel(
    "Price of cryptocurrency",
    -90
  );

  var postDataXAxis = new Plottable.Axes.Numeric(xScale, "bottom");
  var postDataYAxis = new Plottable.Axes.Numeric(postDataYScale, "left");
  var postDataLabel = new Plottable.Components.AxisLabel(
    "Score on single post",
    -90
  );

  var socialMediaDataXAxis = new Plottable.Axes.Numeric(xScale, "bottom");
  var socialMediaDataYAxis = new Plottable.Axes.Numeric(
    socialMediaDataYScale,
    "left"
  );
  var socialMediaLabel = new Plottable.Components.AxisLabel(
    "Activity of community",
    -90
  );

  var chart1 = new Plottable.Components.Table([
    [marketDataLabel, marketDataYAxis, marketDataPlot],
    [null, null, marketDataXAxis]
  ]);

  var chart2 = new Plottable.Components.Table([
    [postDataLabel, postDataYAxis, postDataPlot],
    [null, null, postDataXAxis]
  ]);

  var chart3 = new Plottable.Components.Table([
    [socialMediaLabel, socialMediaDataYAxis, socialMediaDataPlot],
    [null, null, socialMediaDataXAxis],
    [null, null, xLabel]
  ]);

  var table = new Plottable.Components.Table([[chart1], [chart2], [chart3]]);

  table.renderTo("svg#plot");
});
