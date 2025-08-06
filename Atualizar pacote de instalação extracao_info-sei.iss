[Setup]
AppName= Extra��o Info - SEI
AppVersion=1.0.0
DefaultDirName={localappdata}\Extra��o Info - SEI
DefaultGroupName=Extra��o Info - SEI
OutputBaseFilename=Extracao_Itens-SEI_Setup
// NÃO MEXA NESSAS OPÇÕES //////////////////
Compression=lzma
SolidCompression=yes
PrivilegesRequired=lowest
/////////////////////////////////////////////
[Files]
Source: "C:\2python\public-extracao-info_sei\dist\extracao_info_sei\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs
// MANTENHA O PADRÃO "\*" NO FINAL DO CAMINHO 
// PARA INDICAR QUE VAI SER UTILIZADO OS ARQUIVOS 
// DAQUELA PASTA EM ESPECIFICO
/////////////////////////////////////////////

// IDIOMA DO INSTALADOR, PADRÃO PORTUGUES ///
[Languages]
Name: "portuguese"; MessagesFile: "compiler:Languages\Portuguese.isl"
/////////////////////////////////////////////
// DECLARAR ATALHOS DO PROGRAMA ((PADRÃO))
[Icons]
Name: "{userdesktop}\Extra��o Info - SEI"; Filename: "{app}\extracao_info-sei.exe"   
Name: "{userdesktop}\Desinstalar Extra��o Itens Almoxarifado - SEI"; Filename: "{uninstallexe}"

// ATALHOS OPCIONAIS DEPENDENDO DO PROGRAMA, COMO PASTA DE DOWNLOAD OU PLANILHAS EXCEL
Name: "{userdesktop}\Planilha Extraidos"; Filename: "{app}\_internal\excel\itens_extraidos.xlsx"
Name: "{userdesktop}\Manual Extra��o Itens Almoxarifado - SEI"; Filename: "{app}\_internal\README.pdf"
/////////////////////////////////////////////
// CODIGO PADRÃO APENAS MUDE A FUNÇÃO DO PROGRAMA
[Code]
var
  CustomPage: TWizardPage;
  TermsPage: TInputOptionWizardPage;
  MemoText: TMemo; // Declara a variável MemoText

procedure InitializeWizard;
begin
  // Cria uma página personalizada
  CustomPage := CreateCustomPage(wpWelcome, 'Informa��es Importantes', 'Leia as informa��es abaixo antes de continuar.');

  // Adiciona um memo na página de informações
  MemoText := TMemo.Create(CustomPage);
  MemoText.Parent := CustomPage.Surface;
  MemoText.ScrollBars := ssVertical; // Adiciona uma barra de rolagem vertical
  MemoText.ReadOnly := True; // Torna o texto somente leitura
  MemoText.WordWrap := True; // Habilita quebra de linha automática
  MemoText.TabStop := False; // Impede que o controle receba foco ao pressionar Tab
  MemoText.Text := 'Este programa n�o armazena nenhuma informa��o como Login, Senha ou dados sens�veis respeitando a LGPD' +
    ' e foi desenvolvido para automatizar Extra��o Info - SEI, ' +
    'permitindo verificar o Processos presente no SEI e gerar rel�rio no formato de Log. Ao utilizar este software, voc� concorda com os seguintes termos:' + #13#10#13#10 +
    '1. Uso Respons�vel: O programa deve ser utilizado apenas para fins legais e autorizados. O usu�rio � respons�vel por garantir que possui permiss�o Extra��o Info - SEI.' + #13#10#13#10 +
    '2. Limita��o de Responsabilidade: O desenvolvedor n�o se responsabiliza por quaisquer danos, perdas ou consequ�ncias decorrentes do uso do programa, incluindo erros no sistema que resultam falhas na automa��o.' + #13#10#13#10 +
    '3. Privacidade e Seguran�a: O programa utiliza credenciais fornecidas pelo usu�rio para realizar login no sistema. O usu�rio � respons�vel por proteger suas credenciais e garantir que elas n�o sejam compartilhadas ou utilizadas de forma inadequada.';
    
  MemoText.Top := 10;
  MemoText.Left := 10;
  MemoText.Width := CustomPage.SurfaceWidth - 20;
  MemoText.Height := CustomPage.SurfaceHeight - 20;

  // Cria uma nova página para os Termos de Uso
  TermsPage := CreateInputOptionPage(CustomPage.ID,
    'Termos de Uso',
    'Leia e aceite os Termos de Uso para continuar',
    'Voc� deve aceitar os Termos de Uso para instalar o programa.',
    True, False);

  // Adiciona a caixa de seleção para aceitar os Termos de Uso
  TermsPage.Add('Eu li e aceito os Termos de Uso.');

  // Define a caixa de seleção como desmarcada por padrão
  TermsPage.Values[0] := False;
end;

function NextButtonClick(CurPageID: Integer): Boolean;
begin
  // Verifica se o usuário está na página de Termos de Uso
  if CurPageID = TermsPage.ID then
  begin
    // Se a caixa de seleção não estiver marcada, exibe uma mensagem de erro
    if not TermsPage.Values[0] then
    begin
      MsgBox('Para instalar esse programa, � necess�rio aceitar os Termos de Uso.', mbError, MB_OK);
      Result := False; // Impede que o usuário avance
      Exit;
    end;
  end;

  Result := True; // Permite que o usuário avance
end;

// O READEME.pdf DEVE SER ESPECIFICAMENTE DO PROGRAMA NO FORMATO PDF
[Run]
Filename: "{app}\_internal\README.pdf"; Description: "Abrir instruções do programa"; Flags: postinstall shellexec skipifsilent
