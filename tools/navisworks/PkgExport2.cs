using System; using System.IO; using System.Linq; using System.Diagnostics;
using Autodesk.Navisworks.Api; using Autodesk.Navisworks.Api.Plugins; using Autodesk.Navisworks.Api.Timeliner;
// 시험용: TimeLiner 작업마다 연결된 부재만 남기고 내보내고, 일정표(tasks.csv)를 같은 폴더에 쓴다.
// 샘플에 공정이 없으면 모델 2단계 항목마다 시험용 작업을 만들어 넣는다.
[Plugin("PkgExport2","IBIM", DisplayName="PkgExport2")]
[AddInPlugin(AddInLocation.AddIn)]
public class PkgExport2 : AddInPlugin {
  public override int Execute(params string[] p) {
    string outDir = p[0]; var csv = new StringWriter(); var log = new StringWriter(); var sw = Stopwatch.StartNew();
    try {
      Document doc = Application.ActiveDocument;
      var rec = Application.Plugins.FindPlugin("NativeExportPluginAdaptor_LcFbxExporterPlugin_Export.Navisworks");
      if(!rec.IsLoaded) rec.LoadPlugin();
      var fbx = rec.LoadedPlugin as Autodesk.Navisworks.Internal.ApiImplementation.NativeExportPluginAdaptor;
      DocumentTimeliner tl = doc.GetTimeliner();
      if(tl.Tasks.Count == 0){
        int i = 0; DateTime d = new DateTime(2027,1,4);
        foreach(var top in doc.Models.First.RootItem.Children) foreach(var k in top.Children){
          if(!k.DescendantsAndSelf.Any(x => x.HasGeometry)) continue;
          i++; var t = new TimelinerTask();
          t.DisplayName = "T" + i.ToString("000") + " " + top.DisplayName + " / " + k.DisplayName;
          t.PlannedStartDate = d; t.PlannedEndDate = d.AddDays(20); d = d.AddDays(9);
          var c = new ModelItemCollection(); c.Add(k); t.Selection.CopyFrom(c); tl.TaskAddCopy(t);
        }
      }
      csv.WriteLine("task_id,name,start,end,type");
      int n = 0, skipped = 0;
      foreach(SavedItem si in tl.Tasks){
        var t = si as TimelinerTask; if(t==null) continue;
        ModelItemCollection sel = t.Selection.GetSelectedItems(doc);
        if(sel.Count==0){ skipped++; log.WriteLine("NO_ATTACHED_ITEMS," + t.DisplayName); continue; }
        n++; string id = "T" + n.ToString("000");
        doc.Models.ResetAllHidden();
        var inv = new ModelItemCollection(); inv.CopyFrom(sel); inv.Invert(doc);
        doc.Models.SetHidden(inv, true);
        fbx.Execute(Path.Combine(outDir, id + ".fbx"));
        string name = t.DisplayName.Replace("\"", "'");
        csv.WriteLine("{0},\"{1}\",{2:yyyy-MM-dd},{3:yyyy-MM-dd},시공", id, name, t.PlannedStartDate, t.PlannedEndDate);
      }
      doc.Models.ResetAllHidden();
      log.WriteLine("exported,{0},skipped,{1},seconds,{2:0.0}", n, skipped, sw.Elapsed.TotalSeconds);
    } catch(Exception e){ log.WriteLine("ERR " + e); }
    File.WriteAllText(Path.Combine(outDir,"tasks.csv"), csv.ToString(), new System.Text.UTF8Encoding(true));
    File.WriteAllText(Path.Combine(outDir,"export_log.txt"), log.ToString(), System.Text.Encoding.UTF8);
    return 0;
  }
}
