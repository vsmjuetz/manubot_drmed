Option Explicit

Private Const PROTECT_PWD As String = "pvs_secure"
Private Const INIT_FLAG As String = "INIT"

'Beim Öffnen Initialisierung starten
Public Sub Workbook_Open()
    ProtectSheets
    InitDropdowns
    SeedData
End Sub

'Alle Blätter schützen und versteckte Blätter ausblenden
Private Sub ProtectSheets()
    Dim ws As Worksheet
    ThisWorkbook.Unprotect Password:=PROTECT_PWD
    ThisWorkbook.Protect Password:=PROTECT_PWD, Structure:=True

    For Each ws In ThisWorkbook.Worksheets
        ws.Unprotect Password:=PROTECT_PWD
        ws.Protect Password:=PROTECT_PWD, UserInterfaceOnly:=True
    Next ws

    Worksheets("Lookups").Visible = xlVeryHidden
    Worksheets("AuditLog").Visible = xlVeryHidden
End Sub

'Dropdown-Werte für Grund anlegen
Private Sub InitDropdowns()
    Dim arrGrund, rng As Range
    arrGrund = Array("Therapie", "Off-Label", "Prävention", "Kosmetik", "Freundschaftlich")
    With Worksheets("Lookups")
        Set rng = .Range("A2").Resize(UBound(arrGrund) + 1, 1)
        rng.Value = Application.Transpose(arrGrund)
    End With

    With Worksheets("Verordnungen").Columns("G").Validation
        .Delete
        .Add Type:=xlValidateList, AlertStyle:=xlValidAlertStop, Operator:=xlBetween, _
             Formula1:="=Lookups!$A$2:$A$6"
    End With
End Sub

'Erstdaten anlegen falls noch nicht vorhanden
Private Sub SeedData()
    Dim lu As Worksheet, p As Worksheet, r As Worksheet
    Set lu = Worksheets("Lookups")
    Set p = Worksheets("Patienten")
    Set r = Worksheets("Verordnungen")

    If lu.Range("B1").Value = INIT_FLAG Then Exit Sub

    'IDs vorbereiten
    lu.Range("B2").Value = 4 'nächste Patienten-ID
    lu.Range("B3").Value = 6 'nächste Rx-ID

    'Patienten-Stammdaten
    p.Cells(2, 1).Resize(3, 6).Value = Array( _
        Array(1, "Udo Kratz", DateSerial(1970, 8, 18), "Freund", "", ""), _
        Array(2, "Eva Schmidt", DateSerial(1985, 2, 2), "Kollegin", "", ""), _
        Array(3, "Tobias Meyer", DateSerial(1990, 11, 11), "Nachbar", "", "") _
    )

    'Beispiel-Verordnungen
    r.Cells(2, 1).Resize(5, 10).Value = Array( _
        Array(1, 1, "Wegovy 2,4 mg", "", 1, DateSerial(2025, 4, 15), "Therapie", "J", "J", ""), _
        Array(2, 1, "Wegovy 2,4 mg", "", 1, DateSerial(2025, 6, 13), "Therapie", "J", "J", ""), _
        Array(3, 1, "Wegovy 2,4 mg", "", 1, DateSerial(2025, 6, 16), "Therapie", "J", "J", ""), _
        Array(4, 2, "Botulinum (A-Kosmetik)", "", 1, DateSerial(2025, 7, 1), "Kosmetik", "J", "J", ""), _
        Array(5, 3, "Vitamin D 5.000 IE", "", 1, DateSerial(2025, 7, 3), "Prävention", "J", "J", "") _
    )

    lu.Range("B1").Value = INIT_FLAG
End Sub

